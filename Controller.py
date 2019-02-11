import os
import sys
import threading

__author__ = 'pezzati'

from Network import *
from AI import AI
from threading import Thread
from queue import Queue


class Controller:
    def __init__(self):
        self.sending_flag = True
        self.conf = {}
        self.network = None
        self.queue = Queue()
        self.world = World(queue=self.queue)
        self.client = AI()
        self.argNames = ["AICHostIP", "AICHostPort", "AICToken", "AICRetryDelay"]
        self.argDefaults = ["127.0.0.1", 7099, "00000000000000000000000000000000", "1000"]
        self.turn_num = 0
        self.preprocess_flag = False

    def start(self):
        self.read_settings()
        self.network = Network(ip=self.conf[self.argNames[0]],
                               port=self.conf[self.argNames[1]],
                               token=self.conf[self.argNames[2]],
                               message_handler=self.handle_message)
        self.network.connect()

        def run():
            while self.sending_flag:
                event = self.queue.get()
                self.queue.task_done()
                message = {
                    'name': Event.EVENT,
                    'args': [{'type': event.type, 'args': event.args}]
                }
                if World.DEBUGGING_MODE and World.LOG_FILE_POINTER is not None:
                    World.LOG_FILE_POINTER.write('------send message to server-----\n ' + message.__str__())
                self.network.send(message)

        Thread(target=run, daemon=True).start()

    def terminate(self):
        if World.LOG_FILE_POINTER is not None:
            World.LOG_FILE_POINTER.write('finished')
            World.LOG_FILE_POINTER.flush()
            World.LOG_FILE_POINTER.close()
        print("finished!")
        self.network.close()
        self.sending_flag = False

    def read_settings(self):
        if os.environ.get(self.argNames[0]) is None:
            for i in range(len(self.argNames)):
                self.conf[self.argNames[i]] = self.argDefaults[i]
        else:
            for i in range(len(self.argNames)):
                self.conf[self.argNames[i]] = os.environ.get(self.argNames[i])

    def handle_message(self, message):
        if message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_INIT:
            self.world._handle_init_message(message)
            threading.Thread(target=self.launch_on_thread(self.client.preprocess, 'init', self.world, [])).start()
        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_PICK:
            new_world = World(world=self.world)
            new_world._handle_pick_message(message)
            threading.Thread(target=self.launch_on_thread(self.client.pick, 'pick', new_world,
                                                          [new_world.current_turn])).start()
        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_TURN:
            new_world = World(world=self.world)
            new_world._handle_turn_message(message)
            if new_world.current_phase == Phase.MOVE:
                threading.Thread(target=self.launch_on_thread(self.client.move, 'move', new_world,
                                                              [new_world.current_turn,
                                                               new_world.move_phase_num])).start()
            elif new_world.current_phase == Phase.ACTION:
                threading.Thread(target=self.launch_on_thread(self.client.action, 'action', new_world,
                                                              [new_world.current_turn])).start()
        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_SHUTDOWN:
            self.terminate()

    def launch_on_thread(self, action, name, new_world, args):
        action(new_world)
        new_world.queue.put(Event(name + '-end', args))


if __name__ == '__main__':
    c = Controller()
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        World.DEBUGGING_MODE = True
    c.start()
