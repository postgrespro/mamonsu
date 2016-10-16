# -*- coding: utf-8 -*-

import os
import optparse
import pwd
import sys

import mamonsu.lib.platform as platform
from mamonsu.plugins.pgsql.checks import is_conn_to_db
from mamonsu import __version__ as mamonsu_version
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.plugins.pgsql.pool import Pooler
from mamonsu.tools.bootstrap.sql import CreateSchemaSQL, QuerySplit


class Args(DefaultConfig):

    def __init__(self):
        parser = optparse.OptionParser(
            usage='%prog bootstrap <DBNAME>',
            version='%prog bootstrap {0}'.format(mamonsu_version),
            description='Bootstrap DDL for monitoring')
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

        self.args, commands = parser.parse_args()

        if len(commands) > 0:
            if len(commands) == 1:
                self.args.dbname = commands[0]
            else:
                parser.print_help()
                sys.exit(1)

        # apply env
        os.environ['PGUSER'] = self.args.username
        os.environ['PGPASSWORD'] = self.args.password
        os.environ['PGHOST'] = self.args.hostname
        os.environ['PGDATABASE'] = self.args.dbname
        os.environ['PGAPPNAME'] = 'mamonsu deploy'

    def try_configure_connect_to_pg(self):
        if not self._configure_auto_host():
            if self._try_run_as_postgres():
                if not self._configure_auto_host():
                    sys.stderr.write(
                        "Can't connect as user postgres,"
                        " may be database settings wrong?\n")
                    return False
            else:
                sys.stderr.write(
                    "Can't connect with host=auto,"
                    " may be database settings wrong?\n")
                return False
        return True

    def _try_run_as_postgres(self):
        if platform.UNIX and os.getegid() == 0:
            try:
                uid = pwd.getpwnam('postgres').pw_uid
                os.seteuid(uid)
                return True
            except Exception as e:
                sys.stderr.write("Failed run as postgres: {0}\n".format(e))
                pass
        return False

    def _configure_auto_host(self):

        def test_db(self, host_pre):
            if is_conn_to_db(
                host=host_pre,
                db=self.args.dbname,
                port=self.args.port,
                user=self.args.username,
                    paswd=self.args.password):
                self.args.hostname = host_pre
                os.environ['PGHOST'] = self.args.hostname
                return True
            return False

        host = self.args.hostname
        port = self.args.port
        if host == 'auto' and platform.UNIX:
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


def run_deploy():

    args = Args()
    if not args.try_configure_connect_to_pg():
        sys.exit(1)

    try:
        for sql in CreateSchemaSQL.split(QuerySplit):
            Pooler.query(sql)
    except Exception as e:
        sys.stderr.write("Query:\n{0}\nerror: {1}\n".format(sql, e))
        sys.exit(2)
