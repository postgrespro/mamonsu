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
from mamonsu.lib.agent import get_api_metric
from mamonsu.lib.agent import get_api_metric_list, get_api_version


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
            return run_report()

    for arg in sys.argv:
        if arg == 'tune':
            sys.argv.remove(arg)
            return run_tune()

    for arg in sys.argv:
        if arg == 'zabbix':
            sys.argv.remove(arg)
            return run_zabbix()

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

    if len(cfg.args.commands) > 0:

        def _print_help():
            msg = 'mamonsu agent '
            msg += '[run|version|metric-get <metric key>|metric-list]\n'
            sys.stderr.write(msg)
            sys.exit(7)

        commands = cfg.args.commands
        if 'agent' == commands[0]:
            if len(commands) <= 1:
                _print_help()
            if 'run' == commands[1]:
                pass
            elif 'version' == commands[1]:
                return get_api_version(cfg)
            elif 'metric-get' == commands[1]:
                if len(commands) == 3:
                    return get_api_metric(cfg, commands[2])
                else:
                    _print_help()
            elif 'metric-list' == commands[1]:
                return get_api_metric_list(cfg)
            else:
                _print_help()
        else:
            _print_help()

    try:
        logging.info("Start agent")
        supervisor.start()
    except KeyboardInterrupt:
        quit_handler()
