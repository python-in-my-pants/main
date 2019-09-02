import time
from _thread import *


class TTimer:

    def __init__(self):
        self.timers = []

    def set_timer(self, index, period):
        self.timers[index] = start_new_thread(self.timer_function_binder(period, index), ())

    def timer_function_binder(self, period, index):

        def threaded_timer():
            time.sleep(period)
            self.timers[index] = 0

        threaded_timer().__name__ = "lel"
        return threaded_timer()
