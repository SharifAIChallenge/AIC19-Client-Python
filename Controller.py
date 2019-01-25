import os
import sys

__author__ = 'pezzati'

from Network import *
from AI import AI
from threading import Thread
from queue import Queue


class Controller():
    def __init__(self):
        self.sending_flag = True
        self.conf = {}
        self.network = None
        self.queue = Queue()
        self.world = World(self.queue)
        self.client = AI()
        self.argNames = ["AICHostIP", "AICHostPort", "AICToken", "AICRetryDelay"]
        self.argDefaults = ["127.0.0.1", 7099, "00000000000000000000000000000000", "1000"]
        self.turn_num = 0

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
                self.network.send(message)

        Thread(target=run, daemon=True).start()

    def terminate(self):
        if World._LOG_FILE_POINTER is not None:
            World._LOG_FILE_POINTER.flush()
            World._LOG_FILE_POINTER.close()
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
        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_TURN:
            self.world._handle_turn_message(message)
            self.do_turn()
        elif message[ServerConstants.KEY_NAME] == ServerConstants.MESSAGE_TYPE_SHUTDOWN:
            self.terminate()
            
    def do_turn(self):
        end_message = self.world._get_end_message()
        self.turn_num += 1
        if self.turn_num % 10 == 0:
            self.client.complex_turn(self.world)
        else:
            self.client.simple_turn(self.world)
        self.world.end_turn(end_message)



c = Controller()
if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
    World._DEBUGGING_MODE = True
c.start()