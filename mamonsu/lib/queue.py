# -*- coding: utf-8 -*-

import threading


class Queue(object):

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def add(self, metric):
        self.lock.acquire()
        self.queue.insert(0, metric)
        self.lock.release()

    # replace last metric
    def replace(self, metric):
        self.lock.acquire()
        self.queue.pop()
        self.queue.append(metric)
        self.lock.release()

    def size(self):
        self.lock.acquire()
        result = len(self.queue)
        self.lock.release()
        return result

    def flush(self):
        self.lock.acquire()
        result, self.queue = self.queue, []
        self.lock.release()
        return result
