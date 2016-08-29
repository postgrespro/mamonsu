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

    def _parse_hash(self, hash_key, host=None):
        result = hash_key.split('{0}_+_'.format(host))
        if len(result) == 1:
            return hash_key
        else:
            return result[1]

    def update_senders(self, senders=[]):
        self._senders = senders

    # resend all values to senders
    def send(self, key, value, delta=None, host=None, clock=None):

        if clock is None:
            clock = int(time.time())

        hash_key = self._hash(key, host)
        if delta is not None:
            is_float = isinstance(value, float)
            is_int = isinstance(value, int)
            if is_float or is_int:
                if hash_key not in self._last_values:
                    self._last_values[hash_key] = (value, clock)
                    return
                else:
                    last_value = self._last_values[hash_key][0]
                    last_time = self._last_values[hash_key][1]
                    self._last_values[hash_key] = (value, clock)
                    if delta == Plugin.DELTA.speed_per_second:
                        value = float(value - last_value)/(clock - last_time)
                    if delta == Plugin.DELTA.simple_change:
                        value = float(value - last_value)
                    if is_int:
                        value = int(value)
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
        hash_key_list, result = self._last_values.keys(), []
        for h in hash_key_list:
            result.append(
                (self._parse_hash(h, host), self._last_values[h])
            )
        return result

    def json(self, val):
        return json.dumps(val)
