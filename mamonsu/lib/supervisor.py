# -*- coding: utf-8 -*-

import time

from mamonsu.lib.sender import *
from mamonsu.lib.senders import *
from mamonsu.tools.agent import *
from mamonsu.plugins import *


class Supervisor(object):

    Running = True

    def __init__(self, config):
        self.Plugins = []
        self.config = config
        self._sender = Sender()
        self._senders = []

    def start(self):
        self._load_plugins()
        self._update_senders()
        self._start_plugins()
        self._loop()

    def _load_plugins(self):
        for klass in Plugin.only_child_subclasses():
            plugin = klass(self.config)
            self.Plugins.append(plugin)

    def _update_senders(self):
        for plugin in self.Plugins:
            plugin.set_sender(self._sender)
            if plugin.is_sender():
                self._sender.add_sender(plugin)

    def _start_plugins(self):
        for plugin in self.Plugins:
            if plugin.is_enabled() and not plugin.is_alive():
                plugin.start()

    def _loop(self):
        plugin_errors, plugin_probes, last_error = 0, 0, ''
        while self.Running:
            for plugin in self.Plugins:
                if plugin.is_enabled() and not plugin.is_alive():
                    plugin.start()
                    last_error = plugin.last_error_text
                    plugin_errors += 1
            time.sleep(10)
            # error counts
            plugin_probes += 1
            if plugin_probes >= 60:
                if plugin_errors > 0:
                    self._sender.send(
                        'mamonsu.plugin.errors[]',
                        'Errors in the last 60 seconds: {0}.\
                        Last error: {1}'.format(
                            plugin_errors, last_error))
                else:
                    self._sender.send('mamonsu.plugin.errors[]', '')
                plugin_errors, plugin_probes = 0, 0
