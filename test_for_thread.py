import threading
import time


class MyTestThread(threading.Thread):

    def run(self):
        while True:
            print("man hanooz daram kar mikonam!")
            time.sleep(1)


class Oonyeki(threading.Thread):
    def run(self):
        while True:
            print("-----man oon yeki am !!!-----")
            time.sleep(1)


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while True:
            print("---- man hanooz zende am !!! ----- ")
            time.sleep(0.5)


file = open("map.map")