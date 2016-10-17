# -*- coding: utf-8 -*-

import logging
import optparse
import os
import sys
import pwd

from mamonsu import __version__
import mamonsu.lib.platform as platform
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.plugins.pgsql.driver.checks import is_conn_to_db
from mamonsu.tools.tune.pgsql import AutoTunePgsl
from mamonsu.tools.tune.system import AutoTuneSystem


class Args(DefaultConfig):

    def __init__(self):

        parser = optparse.OptionParser(
            usage='%prog tune',
            version='%prog tune {0}'.format(__version__),
            description='Tune config')
        group = optparse.OptionGroup(
            parser,
            'Start options')
        if platform.LINUX:
            group.add_option(
                '--disable-sudo',
                dest='disable_sudo', action='store_false',
                help='Disable sudo')
        group.add_option(
            '--dry-run',
            dest='dry_run', action='store_true',
            help='Dry run')
        group.add_option(
            '--dont-tune-pgbadger',
            dest='pgbadger', action='store_true',
            help='Don\'t configure pgBadger log settings')
        group.add_option(
            '--dont-reload-postgresql',
            dest='reload_config', action='store_true',
            help='Don\'t reload config')
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

    def try_configure_connect_to_pg(self):
        if not self._configure_auto_host():
            if self._try_run_as_postgres():
                if not self._configure_auto_host():
                    logging.error('Can\'t run as postgres')
                    return False
            else:
                logging.error('Can\'t configure auto-host for postgresql')
                return False
        return True

    def _try_run_as_postgres(self):
        if platform.LINUX and os.getegid() == 0:
            try:
                uid = pwd.getpwnam('postgres').pw_uid
                os.seteuid(uid)
                return True
            except Exception as e:
                logging.error('Failed run as postgres: {0}'.format(e))
                pass
        return False

    def _configure_auto_host(self):

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
        if host == 'auto' and platform.UNIX:
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


def run_tune():
    args = Args()
    AutoTuneSystem(args)
    if not args.try_configure_connect_to_pg():
        sys.exit(3)
    AutoTunePgsl(args)
