# -*- coding: utf-8 -*-

import time
from threading import Thread
import logging

from mamonsu.lib.const import Template


class Plugin(object):

    # plugin interval run
    Interval = 60

    _thread = None
    _sender = False
    _enabled = True

    # const
    DELTA = Template.DELTA
    GRAPH_TYPE = Template.GRAPH_TYPE
    VALUE_TYPE = Template.VALUE_TYPE
    UNITS = Template.UNITS

    DELTA_SPEED = Template.DELTA.speed_per_second
    DELTA_CHANGE = Template.DELTA.simple_change

    def __init__(self, config):
        self.config = config
        self.log = logging.getLogger(
            self.__class__.__name__.upper())
        self.sender = None
        self.last_error_text = ''

    def start(self):
        self._thread = Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def is_alive(self):
        if self._thread is not None:
            return self._thread.is_alive()
        return False

    def run(self, sender):
        return None

    def is_sender(self):
        return self._sender

    def is_enabled(self):
        return self._enabled

    def update_sender(self, sender):
        self.sender = sender

    def items(self, template):
        return None

    def graphs(self, template):
        return None

    def triggers(self, template):
        return None

    def discovery_rules(self, template):
        return None

    def _log_exception(self, e):
        name = e.__class__.__name__
        self.last_error_text = 'Plugin exception [{0}]: {1}'.format(name, e)
        self.log.error(self.last_error_text)

    def _loop(self):
        while(True):
            last_start = time.time()
            try:
                self.run(self.sender)
            except Exception as e:
                self._log_exception(e)
                return
            sleep_time = self.Interval - int(time.time() - last_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                self.log.error(
                    'Timeout: {0}s'.format(int(time.time() - last_start)))
                return
