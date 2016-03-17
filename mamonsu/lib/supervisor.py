# -*- coding: utf-8 -*-

import time
import logging
import signal
import sys

import mamonsu.lib.platform as platform
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.config import Config
from mamonsu.lib.zbx import *
from mamonsu.plugins import *


class Supervisor(object):

    Running = True

    def __init__(self, config):
        self.Plugins = []
        self.config = config
        self.sender = None

    def start(self):
        self._load_plugins()
        self._find_sender()
        self._update_plugins()
        self._loop()

    def _load_plugins(self):
        for klass in Plugin.__subclasses__():
            plugin = klass(self.config)
            self.Plugins.append(plugin)

    def _find_sender(self):
        for plugin in self.Plugins:
            if plugin.is_sender():
                if self.sender is not None:
                    raise RuntimeError("Sender already setted")
                self.sender = plugin
        if self.sender is None:
            raise RuntimeError("Can't find sender")

    def _update_plugins(self):
        for plugin in self.Plugins:
            plugin.update_sender(self.sender)

    def _loop(self):
        while self.Running:
            for plugin in self.Plugins:
                if not plugin.is_alive():
                    plugin.start()
            time.sleep(1)


def start(blocking=False):

    def quit_handler(_signo=None, _stack_frame=None):
        logging.info("Bye bye!")
        sys.exit(0)

    signal.signal(signal.SIGTERM, quit_handler)
    if platform.LINUX:
        signal.signal(signal.SIGQUIT, quit_handler)

    config = Config()
    supervisor = Supervisor(config)

    try:
        logging.info("Start agent")
        supervisor.start()
    except KeyboardInterrupt:
        quit_handler()
