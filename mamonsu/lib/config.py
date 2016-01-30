# -*- coding: utf-8 -*-

import optparse
import socket
import os
import logging
import sys

import mamonsu.lib.platform as platform

from mamonsu import __version__
from mamonsu.plugins import Loader as PluginLoader
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

        parser.add_option(
            '-c', '--config',
            dest='config',
            default=None,
            help='Path to config file')

        parser.add_option(
            '-p', '--pid',
            dest='pid',
            default=None,
            help='Path to pid file')

        parser.add_option(
            '-w',
            '--write-config-file',
            dest='write_config_file',
            default=None,
            help='Write default config to file and exit')

        parser.add_option(
            '-e',
            '--export-template-file',
            dest='write_template_file',
            default=None,
            help='Write template to file and exit')

        parser.add_option(
            '-t',
            '--template',
            dest='template',
            default='PostgrePro-{0}'.format(sys.platform.title()),
            help='Generated template name')

        parser.add_option(
            '-a',
            '--application',
            dest='application',
            default='App-PostgrePro-{0}'.format(sys.platform.title()),
            help='Application for generated template')

        if platform.WINDOWS:
            SERVICE_NAME = 'mamonsu'
            SERVICE_DESC = 'Zabbix active agent mamonsu'
            parser.add_option(
                '-r',
                '--register',
                dest='register',
                default=None,
                help='Register as windows service with params')
            parser.add_option(
                '-u',
                '--unregister',
                dest='unregister',
                action='store_true', default=False,
                help='Unregister windows service')

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

        if args.config and not os.path.isfile(args.config):
            print('Config file {0} not found'.format(args.config))
            sys.exit(1)
        else:
            if args.config is not None:
                config.read(args.config)
        self.config = config

        logging.basicConfig(
            format=self.fetch('log', 'format', raw=True),
            filename=self.fetch('log', 'file'),
            level=self.get_logger_level(self.fetch('log', 'level')))

        if args.write_config_file is not None:
            with open(args.write_config_file, 'w') as configfile:
                config.write(configfile)
                sys.exit(0)

        if args.write_template_file is not None:
            plugins = []
            PluginLoader.load()
            for klass in Plugin.__subclasses__():
                plugins.append(klass(self))
            template = ZbxTemplate(args.template, args.application)
            with open(args.write_template_file, 'w') as templatefile:
                templatefile.write(template.xml(plugins))
                sys.exit(0)

        if platform.WINDOWS:
            from mamonsu.lib.win32service import ServiceControlManagerContext
            from mamonsu.lib.win32service import ServiceType, ServiceStartType
            if args.register:
                with ServiceControlManagerContext() as scm:
                    scm.create_service(
                        SERVICE_NAME,
                        SERVICE_DESC,
                        ServiceType.WIN32_OWN_PROCESS,
                        ServiceStartType.AUTO,
                        '{0} {1}'.format(__file__, args.register),
                    )
                sys.exit(0)
            if args.unregister:
                with ServiceControlManagerContext() as scm:
                    scm.delete_service(SERVICE_NAME)
                sys.exit(0)

        if args.pid is not None:
            with open(args.pid, 'w') as pidfile:
                pidfile.write(str(os.getpid()))

        os.environ['PGUSER'] = self.fetch('postgres', 'user')
        if self.fetch('postgres', 'password'):
            os.environ['PGPASSWORD'] = self.fetch('postgres', 'password')
        os.environ['PGHOST'] = self.fetch('postgres', 'host')
        os.environ['PGPORT'] = str(self.fetch('postgres', 'port'))
        os.environ['PGDATABASE'] = self.fetch('postgres', 'database')
        os.environ['PGTIMEOUT'] = self.fetch('postgres', 'query_timeout')

    # function fetch value of key in section
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
