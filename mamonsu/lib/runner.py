# -*- coding: utf-8 -*-

import logging
import signal
import sys
import codecs
import os

import mamonsu.lib.platform as platform
from mamonsu.lib.config import Config
from mamonsu.lib.supervisor import Supervisor
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.zbx_template import ZbxTemplate

from mamonsu.tools.report.start import run_report
from mamonsu.tools.tune.start import run_tune
from mamonsu.tools.zabbix_cli.start import run_zabbix


def start():

    def quit_handler(_signo=None, _stack_frame=None):
        logging.info("Bye bye!")
        sys.exit(0)

    signal.signal(signal.SIGTERM, quit_handler)
    if platform.LINUX:
        signal.signal(signal.SIGQUIT, quit_handler)

    for arg in sys.argv:
        if arg == 'report':
            sys.argv.remove(arg)
            run_report()
            return

    for arg in sys.argv:
        if arg == 'tune':
            sys.argv.remove(arg)
            run_tune()
            return

    for arg in sys.argv:
        if arg == 'zabbix':
            sys.argv.remove(arg)
            run_zabbix()
            return

    cfg = Config()

    # config
    if cfg.args.write_config_file is not None:
        with open(cfg.args.write_config_file, 'w') as fd:
            cfg.config.write(fd)
            sys.exit(0)

    # template
    if cfg.args.template_file is not None:
        plugins = []
        for klass in Plugin.get_childs():
            plugins.append(klass(cfg))
        template = ZbxTemplate(cfg.args.template, cfg.args.application)
        with codecs.open(cfg.args.template_file, 'w', 'utf-8') as f:
            f.write(template.xml(plugins))
            sys.exit(0)

    supervisor = Supervisor(cfg)

    # write pid file
    if cfg.args.pid is not None:
        try:
            with open(cfg.args.pid, 'w') as pidfile:
                pidfile.write(str(os.getpid()))
        except Exception as e:
            sys.stderr.write('Can\'t write pid file, error: %s'.format(e))
            sys.exit(2)

    try:
        logging.info("Start agent")
        supervisor.start()
    except KeyboardInterrupt:
        quit_handler()
