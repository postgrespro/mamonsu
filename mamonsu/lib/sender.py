# -*- coding: utf-8 -*-
import json
import time

from mamonsu.lib.plugin import Plugin


class Sender():

    def __init__(self):
        self._senders = []
        self._last_values = {}

    def _hash(self, key, host=None):
        return '{0}_+_{1}'.format(host, key)

    def _key_from_hash(self, hash, host=None):
        result = hash.split('{0}_+_'.format(host))
        if len(result) == 1:
            return hash
        else:
            return result[1]

    def add_sender(self, sender):
        self._senders.append(sender)

    # resend all values to senders
    def send(self, key, value, delta=None, host=None, clock=None):

        if clock is None:
            clock = int(time.time())

        hash_key = self._hash(key, host)
        if delta is not None:
            if isinstance(value, float) or isinstance(value, int):
                if hash_key in self._last_values:
                    last_value, last_time = self._last_values[hash_key]
                    self._last_values[hash_key] = (value, clock)
                    if delta == Plugin.DELTA.speed_per_second:
                        value = float(value - last_value) / (clock - last_time)
                    if delta == Plugin.DELTA.simple_change:
                        value = float(value - last_value)
                else:
                    self._last_values[hash_key] = (value, clock)
                    return
        else:
            self._last_values[hash_key] = (value, clock)

        for sender in self._senders:
            if sender.is_enabled():
                sender.send(key, value, host, clock)

    # get last value: (value, clock)
    def get_metric(self, key, host=None):
        hash_key = self._hash(key, host)
        if hash_key in self._last_values:
            return self._last_values[hash_key]
        else:
            return (None, None)

    # list of metrics: [(key, (value, clock))]
    def list_metrics(self, host=None):
        hash_list, result = self._last_values.keys(), []
        for h in hash_list:
            result.append(
                (self._key_from_hash(h, host), self._last_values[h])
            )
        return result

    def json(self, val):
        return json.dumps(val)
