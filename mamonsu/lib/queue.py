# -*- coding: utf-8 -*-

import threading


class Queue(object):

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def add(self, metric):
        with self.lock:
            self.queue.insert(0, metric)

    # replace last metric
    def replace(self, metric):
        with self.lock:
            if self.queue:
                self.queue.pop()
            self.queue.append(metric)

    def size(self):
        with self.lock:
            return len(self.queue)

    def flush(self):
        with self.lock:
            result, self.queue = self.queue, []
            return result
