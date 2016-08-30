# -*- coding: utf-8 -*-
import socket
import os
import logging
import sys
import glob

import mamonsu.lib.platform as platform
from mamonsu.plugins.pgsql.checks import is_conn_to_db
from mamonsu.lib.default_config import DefaultConfig

if platform.PY2:
    import ConfigParser as configparser
else:
    import configparser


class Config(DefaultConfig):

    def __init__(self, cfg_file=None):

        config = configparser.ConfigParser()

        config.add_section('postgres')
        config.set('postgres', 'enabled', str(True))
        config.set('postgres', 'user', Config.default_user())
        config.set('postgres', 'password', str(Config.default_pgpassword()))
        config.set('postgres', 'database', Config.default_db())
        config.set('postgres', 'host', Config.default_host())
        config.set('postgres', 'port', str(Config.default_port()))
        config.set('postgres', 'application_name', str(Config.default_app()))
        config.set('postgres', 'max_checkpoints_req', '5')
        config.set('postgres', 'query_timeout', '10')
        config.set('postgres', 'uptime', str(60 * 10))
        config.set('postgres', 'cache', str(80))

        config.add_section('system')
        config.set('system', 'enabled', str(True))
        config.set('system', 'uptime', str(60*5))
        config.set('system', 'vfs_percent_free', str(10))
        config.set('system', 'vfs_inode_percent_free', str(10))

        config.add_section('plugins')
        config.set('plugins', 'enabled', str(False))
        config.set('plugins', 'directory', '/etc/mamonsu/plugins')

        config.add_section('sender')
        config.set('sender', 'queue', str(300))

        config.add_section('agent')
        config.set('agent', 'enabled', str(True))
        config.set('agent', 'host', '127.0.0.1')
        config.set('agent', 'port', str(10052))

        config.add_section('zabbix')
        config.set('zabbix', 'enabled', str(True))
        config.set('zabbix', 'client', socket.gethostname())
        config.set('zabbix', 'address', '127.0.0.1')
        config.set('zabbix', 'port', str(10051))

        config.add_section('metric_log')
        config.set('metric_log', 'enabled', str(False))
        config.set('metric_log', 'directory', '/var/log/mamonsu')
        config.set('metric_log', 'max_size_mb', '1024')

        config.add_section('log')
        config.set('log', 'file', str(None))
        config.set('log', 'level', 'INFO')
        config.set(
            'log', 'format',
            '[%(levelname)s] %(asctime)s - %(name)s\t-\t%(message)s')

        self.config = config
        if cfg_file and not os.path.isfile(cfg_file):
            sys.exit(1)
        else:
            if cfg_file is not None:
                self.config.read(cfg_file)

        self._apply_log_setting()
        self._apply_environ()
        self._load_additional_plugins()
        self._override_auto_variables()

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
        os.environ['PGAPPNAME'] = self.fetch('postgres', 'application_name')

    def _apply_log_setting(self):
        logging.basicConfig(
            format=self.fetch('log', 'format', raw=True),
            filename=self.fetch('log', 'file'),
            level=self.get_logger_level(self.fetch('log', 'level')))

    def _load_additional_plugins(self):

        if not self.fetch('plugins', 'enabled', bool):
            return

        directory = self.fetch('plugins', 'directory')
        if not os.path.isdir(directory):
            logging.error("Can't find directory: %s", directory)
            sys.exit(3)

        sys.path.append(directory)
        logging.info(
            'Import module \'%s\' from directory %s',
            os.path.basename(directory),
            directory)

        try:
            for filename in glob.glob(os.path.join(directory, '*.py')):
                if not os.path.isfile(filename):
                    continue
                # /dir/filename.py => filename.py
                filename = os.path.basename(filename)
                if filename.startswith('_'):
                    continue
                # filename.py => filename
                filename, _ = os.path.splitext(filename)
                logging.info(
                    'Import plugin \'%s\' from module \'%s\'',
                    filename,
                    os.path.basename(directory))
                __import__(filename)
        except Exception as e:
            logging.error(
                'Can\'t load module: %s', e)
            sys.exit(3)

    def _override_auto_variables(self):
        self._override_auto_host()

    def _override_auto_host(self):

        def test_db(self, host_pre):
            if is_conn_to_db(
                host=host_pre,
                db=self.fetch('postgres', 'database'),
                port=str(self.fetch('postgres', 'port')),
                user=self.fetch('postgres', 'user'),
                    paswd=self.fetch('postgres', 'password')):
                self.config.set('postgres', 'host', host_pre)
                self._apply_environ()
                return True
            return False

        host = self.fetch('postgres', 'host')
        port = str(self.fetch('postgres', 'port'))
        if host == 'auto' and platform.LINUX:
            logging.debug('Host set to auto, test variables')
            if test_db(self, '/tmp/.s.PGSQL.{0}'.format(port)):
                return
            if test_db(self, '/var/run/postgresql/.s.PGSQL.{0}'.format(port)):
                return
            if test_db(self, '127.0.0.1'):
                return
            #  не выходим, так как ожидаем коннекта до localhost
            self.config.set('postgres', 'host', 'localhost')
            self._apply_environ()
