# -*- coding: utf-8 -*-

import logging
import optparse
import os
try:
    import pwd
except ImportError:
    pass

from mamonsu import __version__
import mamonsu.lib.platform as platform
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.plugins.pgsql.checks import is_conn_to_db

from mamonsu.first_look.pgsql import PostgresInfo
if platform.LINUX:
    from mamonsu.first_look.os_linux import SystemInfo
else:
    from mamonsu.first_look.os_win import SystemInfo


class Args(DefaultConfig):

    def __init__(self):

        parser = optparse.OptionParser(
            usage='%prog first-look',
            version='%prog first-look {0}'.format(__version__),
            description='First look report')
        group = optparse.OptionGroup(
            parser,
            'Start options')
        group.add_option(
            '--run-system',
            dest='run_system',
            default=True, help='Enable system collect (default: %default)')
        group.add_option(
            '--run-postgres',
            dest='run_postgres',
            default=True,
            help='Run postresql collect (default: %default)')
        group.add_option(
            '-l', '--log-level',
            dest='log_level',
            default='INFO', help='Log level (default: %default)')
        if platform.LINUX:
            group.add_option(
                '-t', '--try-connect-as-user-postgres',
                dest='try_postgres',
                default=True,
                help='Try connect as unix user postgres'
                ' (only with auto opts, default: %default)')
        parser.add_option_group(group)
        group = optparse.OptionGroup(
            parser,
            'Report options')
        group.add_option(
            '-w', '--report-path',
            dest='report_path',
            default=self.default_report_path(),
            help='Path to report (default: %default)')
        group.add_option(
            '-r', '--print-report',
            dest='print_report',
            default=True, help='Print summary info (default: %default)')
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
            filename=self.args.report_path,
            level=self.get_logger_level(self.args.log_level))
        # apply env
        os.environ['PGUSER'] = self.args.username
        os.environ['PGPASSWORD'] = self.args.password
        os.environ['PGHOST'] = self.args.hostname
        os.environ['PGDATABASE'] = self.args.dbname
        os.environ['PGAPPNAME'] = 'mamonsu first look'

        if not self._configure_auto_host():
            if self._try_run_as_postgres():
                if not self._configure_auto_host():
                    logging.error('Miss postgres config')
                    self.run_postgres = False
            else:
                logging.error('Miss postgres config')
                self.run_postgres = False

    def _configure_auto_host(self):
        if self.args.run_postgres and not self._auto_host_is_working():
            return False
        return True

    def _try_run_as_postgres(self):
        if platform.LINUX and os.getegid() == 0:
            try:
                uid = pwd.getpwnam('postgres').pw_uid()
                os.seteuid(uid)
                return True
            except:
                pass
        return False

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


def run_first_look():

    args = Args()

    if args.run_system:
        sys_info = SystemInfo(args)
        sys_report = sys_info.collect()
    if args.run_postgres:
        pg_info = PostgresInfo(args)
        pg_report = pg_info.collect()

    if args.print_report:
        if args.run_system:
            print(sys_report)
        else:
            print('Disabled system collect')
        if args.run_postgres:
            print(pg_report)
        else:
            print('Disabled postgres collect')
