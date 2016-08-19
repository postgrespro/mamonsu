# -*- coding: utf-8 -*-

import time
import logging
import signal
import sys

from mamonsu.first_look.start import run_first_look
from mamonsu.auto_tune.start import run_auto_tune
import mamonsu.lib.platform as platform
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.config import Config
from mamonsu.lib.sender import *
from mamonsu.lib.senders import *
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
        self._find_senders()
        self._set_senders()
        self._loop()

    def _load_plugins(self):
        for klass in Plugin.childs():
            plugin = klass(self.config)
            self.Plugins.append(plugin)

    def _find_senders(self):
        for plugin in self.Plugins:
            if plugin.is_sender():
                self._senders.append(plugin)
        if len(self._senders) == 0:
            raise RuntimeError('Can\'t find any senders')

    def _set_senders(self):
        for plugin in self.Plugins:
            plugin.update_sender(self._sender)
        self._sender.update_senders(self._senders)

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


def start():

    def quit_handler(_signo=None, _stack_frame=None):
        logging.info("Bye bye!")
        sys.exit(0)

    signal.signal(signal.SIGTERM, quit_handler)
    if platform.LINUX:
        signal.signal(signal.SIGQUIT, quit_handler)

    for arg in sys.argv:
        if arg == '--run-first-look' or arg == '--run-look'\
                or arg == 'first' or arg == '--first'\
                or arg == 'first-look' or arg == 'report':
            sys.argv.remove(arg)
            run_first_look()
            return

    for arg in sys.argv:
        if arg == 'auto-tune' or arg == '--auto-tune'\
                or arg == 'tune' or arg == 'autotune'\
                or arg == '--autotune':
            sys.argv.remove(arg)
            run_auto_tune()
            return

    config = Config()
    supervisor = Supervisor(config)

    try:
        logging.info("Start agent")
        supervisor.start()
    except KeyboardInterrupt:
        quit_handler()
