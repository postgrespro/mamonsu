# -*- coding: utf-8 -*-

import logging
import optparse
import os
import mamonsu.lib.platform as platform
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.plugins.pgsql.checks import is_conn_to_db

from mamonsu import __version__
if platform.LINUX:
    from mamonsu.lib.first_look_os_linux import SystemInfo
else:
    from mamonsu.lib.first_look_os_win import SystemInfo


class Args(DefaultConfig):

    def __init__(self):

        parser = optparse.OptionParser(
            version='%prog first-look {0}'.format(__version__),
            description='First look report [default: %default]')
        group = optparse.OptionGroup(
            parser,
            'Start options')
        group.add_option(
            '-l', '--log-level',
            dest='log_level',
            default='INFO', help='Log level [default: %default]')
        parser.add_option_group(group)
        group = optparse.OptionGroup(
            parser,
            'Report options')
        group.add_option(
            '-w', '--report-path',
            dest='report_path',
            default=self.default_report_path(),
            help='Path to report [default: %default]')
        group.add_option(
            '-r', '--print-report',
            dest='print_report',
            default=True, help='Print summary info [default: %default]')
        parser.add_option_group(group)
        group = optparse.OptionGroup(
            parser,
            'Postgres connection options')
        group.add_option(
            '--miss-postgres',
            dest='miss_postgres',
            default=False,
            help='Disable postresql checks [default: %default]')
        group.add_option(
            '-d', '--dbname',
            dest='dbname',
            default=self.default_db(),
            help='database name to connect to [default: %default]')
        group.add_option(
            '--host',
            dest='hostname',
            default=self.default_host(),
            help='database server host or socket path [default: %default]')
        group.add_option(
            '-U', '--username',
            dest='username',
            default=self.default_user(),
            help='database user name [default: %default]')
        group.add_option(
            '-W', '--password',
            dest='password',
            default=self.default_user(),
            help='password (should happen automatically) ')
        parser.add_option_group(group)

        self.args, _ = parser.parse_args()

        # apply logging
        logging.basicConfig(
            filename=self.args.report_path,
            level=self.get_logger_level(self.args.log_level))
        # apply env
        os.environ['PGUSER'] = self.args.username
        os.environ['PGPASSWORD'] = self.args.password
        os.environ['PGHOST'] = self.args.hostname
        os.environ['PGDATABASE'] = self.args.database
        os.environ['PGAPPNAME'] = 'mamonsu first look'

        if not self._auto_host_is_working():
            logging.error(
                'Miss postgres checking, can\'t connected with auto options')
            self.args.miss_postgres = True

    def _auto_host_is_working(self):

        def test_db(self, host_pre):
            logging.debug('Test host: {0}'.format(host_pre))
            if is_conn_to_db(
                host=host_pre,
                db=self.args.database,
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

    @staticmethod
    def get_logger_level(level):
        result = logging.INFO
        level = level.upper()
        if level == 'DEBUG':
            return logging.DEBUG
        if level == 'WARNING' or level == 'WARN':
            return logging.WARN
        return result


def run_first_look():
    args = Args()
    info = SystemInfo(args)
    info.run()
