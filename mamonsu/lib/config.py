# -*- coding: utf-8 -*-

import optparse
import socket
import os
import logging
import sys

import mamonsu.lib.platform as platform

from mamonsu import __version__
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.template import *

if platform.PY2:
    import ConfigParser as configparser
else:
    import configparser


class Config(object):

    @staticmethod
    def default_user():
        user = os.environ.get('PGUSER') or os.environ.get('USER') or 'postgres'
        return user

    @staticmethod
    def default_pgpassword():
        password = os.environ.get('PGPASSWORD')
        return password

    @staticmethod
    def default_host():
        host = os.environ.get('PGHOST') or 'localhost'
        return host

    @staticmethod
    def default_port():
        port = int(os.environ.get('PGPORT') or 5432)
        return port

    @staticmethod
    def default_db():
        database = os.environ.get('PGDATABASE') or os.environ.get('PGUSER')
        database = database or os.environ.get('USER') or 'postgres'
        return database

    @staticmethod
    def get_logger_level(level):
        result = logging.INFO
        level = level.upper()
        if level == 'DEBUG':
            return logging.DEBUG
        if level == 'WARNING' or level == 'WARN':
            return logging.WARN
        return result

    def __init__(self):

        parser = optparse.OptionParser(
            usage='%prog [-c] [-p]',
            version='%prog {0}'.format(__version__))

        group = optparse.OptionGroup(
            parser,
            'Start options')
        group.add_option(
            '-c',
            dest='config',
            default=None,
            help='Path to config file')
        group.add_option(
            '-p',
            dest='pid',
            default=None,
            help='Path to pid file')
        parser.add_option_group(group)

        group = optparse.OptionGroup(
            parser,
            'Example options',
            'Export default options')
        group.add_option(
            '-w',
            dest='config_file',
            default=None,
            help='Write default config to file and exit')
        parser.add_option_group(group)

        group = optparse.OptionGroup(
            parser,
            'Export to zabbix',
            'Export zabbix template options')
        group.add_option(
            '-e',
            dest='template_file',
            default=None,
            help='Write template to file and exit')
        group.add_option(
            '-t',
            dest='template',
            default='PostgresPro-{0}'.format(sys.platform.title()),
            help='Generated template name')
        group.add_option(
            '-a',
            dest='application',
            default='App-PostgresPro-{0}'.format(sys.platform.title()),
            help='Application for generated template')
        parser.add_option_group(group)

        args, _ = parser.parse_args()

        config = configparser.ConfigParser()

        config.add_section('template')
        config.set('template', 'name', args.template)
        config.set('template', 'application', args.application)

        config.add_section('postgres')
        config.set('postgres', 'user', Config.default_user())
        config.set('postgres', 'password', str(Config.default_pgpassword()))
        config.set('postgres', 'database', Config.default_db())
        config.set('postgres', 'host', Config.default_host())
        config.set('postgres', 'port', str(Config.default_port()))
        config.set('postgres', 'query_timeout', '10')

        config.add_section('log')
        config.set('log', 'file', str(None))
        config.set('log', 'level', 'INFO')
        config.set(
            'log',
            'format',
            '[%(levelname)s] %(asctime)s - %(name)s\t-\t%(message)s')

        config.add_section('zabbix')
        config.set('zabbix', 'client', socket.gethostname())
        config.set('zabbix', 'address', '127.0.0.1')
        config.set('zabbix', 'port', str(10051))

        config.add_section('sender')
        config.set('sender', 'queue', str(300))

        config.add_section('health')
        config.set('health', 'uptime', str(60 * 10 * 100))
        config.set('health', 'cache', str(80))

        config.add_section('bgwriter')
        config.set('bgwriter', 'max_checkpoints_req', '5')

        self.config = config
        self.load_and_apply_config_file(args.config)

        if args.config_file is not None:
            with open(args.config_file, 'w') as fd:
                config.write(fd)
                sys.exit(0)

        if args.template_file is not None:
            plugins = []
            for klass in Plugin.__subclasses__():
                plugins.append(klass(self))
            template = ZbxTemplate(args.template, args.application)
            with open(args.template_file, 'w') as templatefile:
                templatefile.write(template.xml(plugins))
                sys.exit(0)

        if args.pid is not None:
            try:
                with open(args.pid, 'w') as pidfile:
                    pidfile.write(str(os.getpid()))
            except Exception as e:
                logging.error('Can\'t write pid file, error: %s'.format(e))
                sys.exit(2)

    def load_and_apply_config_file(self, config_file=None):
        if config_file and not os.path.isfile(config_file):
            sys.exit(1)
        else:
            if config_file is not None:
                self.config.read(config_file)
        self._apply_log_setting()
        self._apply_environ()

    def fetch(self, sec, key, klass=None, raw=False):
        try:
            if klass == float:
                return self.config.getfloat(sec, key)
            if klass == int:
                return self.config.getint(sec, key)
            if klass == bool:
                return self.config.getboolean(sec, key)
            if self.config.get(sec, key, raw=raw) == 'None':
                return None
            return self.config.get(sec, key, raw=raw)
        except KeyError:
            return None

    def _apply_environ(self):
        os.environ['PGUSER'] = self.fetch('postgres', 'user')
        if self.fetch('postgres', 'password'):
            os.environ['PGPASSWORD'] = self.fetch('postgres', 'password')
        os.environ['PGHOST'] = self.fetch('postgres', 'host')
        os.environ['PGPORT'] = str(self.fetch('postgres', 'port'))
        os.environ['PGDATABASE'] = self.fetch('postgres', 'database')
        os.environ['PGTIMEOUT'] = self.fetch('postgres', 'query_timeout')

    def _apply_log_setting(self):
        logging.basicConfig(
            format=self.fetch('log', 'format', raw=True),
            filename=self.fetch('log', 'file'),
            level=self.get_logger_level(self.fetch('log', 'level')))
