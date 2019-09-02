import time
from _thread import *


class Timer:

    def __init__(self):
        self.timers = []

    def set_timer(self, index, period):
        self.timers[index] = start_new_thread(self.threaded_timer(period, index), ())

    def threaded_timer(self, period, index):
        time.sleep(period)
        self.timers[index] = 0
