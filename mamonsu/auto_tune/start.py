# -*- coding: utf-8 -*-

import logging
import optparse
import os
import sys

from mamonsu import __version__
import mamonsu.lib.platform as platform
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.plugins.pgsql.checks import is_conn_to_db
from mamonsu.auto_tune.pgsql import AutoTune


class Args(DefaultConfig):

    def __init__(self):

        parser = optparse.OptionParser(
            usage='%prog autotune',
            version='%prog autotune {0}'.format(__version__),
            description='Autotune config')
        group = optparse.OptionGroup(
            parser,
            'Start options')
        group.add_option(
            '--pgbadger',
            dest='pgbadger',
            default=True,
            help='Configure pgBadger log settings (default: %default)')
        group.add_option(
            '-r', '--reload',
            dest='reload_config',
            default=True, help='Reload config (default: %default)')
        group.add_option(
            '-l', '--log-level',
            dest='log_level',
            default='INFO', help='Log level (default: %default)')
        parser.add_option_group(group)
        group = optparse.OptionGroup(
            parser,
            'Postgres connection options')
        group.add_option(
            '-d', '--dbname',
            dest='dbname',
            default=self.default_db(),
            help='database name to connect to (default: %default)')
        group.add_option(
            '--host',
            dest='hostname',
            default=self.default_host(),
            help='database server host or socket path (default: %default)')
        group.add_option(
            '--port',
            dest='port',
            default=self.default_port(),
            help='database server port (default: %default)')
        group.add_option(
            '-U', '--username',
            dest='username',
            default=self.default_user(),
            help='database user name (default: %default)')
        group.add_option(
            '-W', '--password',
            dest='password',
            default=self.default_user(),
            help='password (should happen automatically) ')
        parser.add_option_group(group)

        self.args, _ = parser.parse_args()

        # apply logging
        logging.basicConfig(
            level=self.get_logger_level(self.args.log_level))
        # apply env
        os.environ['PGUSER'] = self.args.username
        os.environ['PGPASSWORD'] = self.args.password
        os.environ['PGHOST'] = self.args.hostname
        os.environ['PGDATABASE'] = self.args.dbname
        os.environ['PGAPPNAME'] = 'mamonsu autotune'

        if not self._auto_host_is_working():
            logging.error(
                'Miss postgres checking, can\'t connected with auto options')
            sys.exit(3)

        if not is_conn_to_db(
            host=self.args.hostname,
            db=self.args.dbname,
            port=self.args.port,
            user=self.args.username,
                paswd=self.args.password):
            logging.error('Can\'t connected to PostgreSQL')
            sys.exit(4)

    def _auto_host_is_working(self):

        def test_db(self, host_pre):
            logging.debug('Test host: {0}'.format(host_pre))
            if is_conn_to_db(
                host=host_pre,
                db=self.args.dbname,
                port=self.args.port,
                user=self.args.username,
                    paswd=self.args.password):
                self.args.hostname = host_pre
                os.environ['PGHOST'] = self.args.hostname
                logging.debug('Connected via: {0}'.format(host_pre))
                return True
            return False
        host = self.args.hostname
        port = self.args.port
        if host == 'auto' and platform.LINUX:
            logging.debug('Host set to auto, test variables')
            if test_db(self, '/tmp/.s.PGSQL.{0}'.format(port)):
                return True
            if test_db(self, '/var/run/postgresql/.s.PGSQL.{0}'.format(port)):
                return True
            if test_db(self, '127.0.0.1'):
                return True
            # auto failed
            return False
        # not auto
        return True

    def __getattr__(self, name):
        try:
            return self.args.__dict__[name]
        except KeyError:
            return None


def run_auto_tune():
    args = Args()
    AutoTune(args)
