# -*- coding: utf-8 -*-

import os
import optparse
import sys

import mamonsu.lib.platform as platform
from mamonsu.lib.parser import MissOptsParser
from mamonsu.plugins.pgsql.driver.checks import is_conn_to_db
from mamonsu import __version__ as mamonsu_version
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.plugins.pgsql.pool import Pooler
from mamonsu.tools.bootstrap.sql import CreateMamonsuUserSQL, CreateSchemaExtensionSQL, \
CreateSchemaDefaultSQL,GrantsOnDefaultSchemaSQL, GrantsOnExtensionSchemaSQL, QuerySplit


class Args(DefaultConfig):

    def __init__(self):
        parser = MissOptsParser(
            usage='%prog bootstrap -M <MAMONSU USERNAME> <DBNAME>',
            version='%prog bootstrap {0}'.format(mamonsu_version),
            description='Bootstrap DDL for monitoring')
        group = optparse.OptionGroup(
            parser,
            'Postgres connection options')
        group.add_option(
            '-d', '--dbname',
            dest='dbname',
            default=None,
            help='database name to connect')
        group.add_option(
            '-h', '--host',
            dest='hostname',
            default=self.default_host(),
            help='database server host or socket path (default: %default)')
        group.add_option(
            '-p', '--port',
            dest='port',
            default=self.default_port(),
            help='database server port (default: %default)')
        group.add_option(
            '-U', '--username',
            dest='username',
            default=self.default_user(),
            help='database superuser name (default: %default)')
        group.add_option(
            '-W', '--password',
            dest='password',
            default='')
        bootstrap_group = optparse.OptionGroup(
            parser,
            'Bootstrap options')
        bootstrap_group.add_option(
            '-v', '--verbose',
            action="store_true",
            dest="verbose",
            default=False,
            help='Show bootstrap DDL')
        bootstrap_group.add_option(
            '-M', '--mamonsu-username',
            dest='mamonsu_username',
            default='mamonsu',
            help='database non-privileged user for mamonsu')
        bootstrap_group.add_option(
            '-x', '--create-extensions',
            action='store_true',
            dest='create_extensions',
            help='create pg_buffercache extension in mamonsu schema')
        parser.add_option_group(group)
        parser.add_option_group(bootstrap_group)

        self.args, commands = parser.parse_args()
        if len(commands) > 0:
            if len(commands) == 1:
                self.args.dbname = commands[0]
            else:
                parser.print_help()
                sys.exit(1)
        if self.args.dbname is None:
            sys.stderr.write("ERROR: Database for mamonsu is not specified\n")
            parser.print_bootstrap_help()
            sys.exit(1)

        if not self.args.dbname:
            self.args.dbname = self.args.username

        # apply env
        os.environ['PGUSER'] = self.args.username
        os.environ['PGPASSWORD'] = self.args.password
        os.environ['PGHOST'] = self.args.hostname
        os.environ['PGPORT'] = str(self.args.port)
        os.environ['PGDATABASE'] = self.args.username if self.args.dbname is None else self.args.dbname
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
                    return True

            else:
                sys.stderr.write(
                    "Can't connect with host=auto,"
                    " may be database settings wrong?\n")
                return False
        else:
            return True

    def _try_run_as_postgres(self):
        if platform.UNIX and os.getegid() == 0:
            try:
                import pwd
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


def fill_query_params(queries):
    formatted_queries = ""
    for sql in queries.format(
            mamonsu_version,
            mamonsu_version.replace('.', '_'),
            '[0-9A-F]{24}',
            'wal' if Pooler.server_version_greater('10.0') else 'xlog',
            'wal_lsn' if Pooler.server_version_greater('10.0') else 'xlog_location',
            'waiting' if Pooler.server_version_less('9.6.0') else 'case when wait_event_type is null then false '
                                                                  ' else true end  as waiting',
            'flush_lag, replay_lag, write_lag,' if Pooler.server_version_greater('10.0') else '',
            'wal_lsn' if Pooler.server_version_greater('10.0') else 'xlog_location',
            'flush_lag INTERVAL, replay_lag INTERVAL, write_lag INTERVAL,' if Pooler.server_version_greater('10.0')
            else '',
            'lsn' if Pooler.server_version_greater('10.0') else 'location',
            'walfile' if Pooler.server_version_greater('10.0') else 'xlogfile'
    ).split(QuerySplit):
        formatted_queries += sql
    return formatted_queries


def fill_grant_params(queries, args):
    formatted_grants_queries = ""
    for sql in queries.format(
            mamonsu_version.replace('.', '_'),
            args.args.mamonsu_username,
            'wal' if Pooler.server_version_greater('10.0') else 'xlog'
    ).split(QuerySplit):
        formatted_grants_queries += sql
    return formatted_grants_queries


def fill_user_params(queries, args):
    formatted_user_queries = ""
    for sql in queries.format(
            args.args.mamonsu_username
    ).split(QuerySplit):
        formatted_user_queries += sql
    return formatted_user_queries


def run_deploy():
    args = Args()

    if not args.try_configure_connect_to_pg():
        sys.stderr.write(str(args.args) + '\n')
        sys.exit(1)

    if not Pooler.is_superuser():
        sys.stderr.write(
            "ERROR: Bootstrap must be run by PostgreSQL superuser\n")
        sys.stderr.write(str(args.args) + '\n')
        sys.exit(1)

    try:
        bootstrap_queries = fill_user_params(CreateMamonsuUserSQL, args)
        Pooler.query(bootstrap_queries)
    except Exception as e:
        sys.stderr.write("Bootstrap execution have exited with an error: {0}\n".format(e))
        sys.exit(2)

    try:
        bootstrap_queries = fill_query_params(CreateSchemaDefaultSQL)
        Pooler.query(bootstrap_queries)
    except Exception as e:
        sys.stderr.write("Bootstrap execution have exited with an error: {0}\n".format(e))
        sys.exit(2)

    if args.args.create_extensions:
        try:
            bootstrap_extension_queries = fill_query_params(CreateSchemaExtensionSQL)
            Pooler.query(bootstrap_extension_queries)
        except Exception as e:
            sys.stderr.write(
                "Bootstrap failed to create pg_buffercache extension and functions.\n"
                "Error: {0}\n".format(e))
            sys.stderr.write("Please install pg_buffercache extension manually and rerun bootstrap "
                             "if you want to get metrics from pg_buffercache view. \n")

    try:
        bootstrap_grant_queries = fill_grant_params(GrantsOnDefaultSchemaSQL, args)
        Pooler.query(bootstrap_grant_queries)

    except Exception as e:
        sys.stderr.write("Error: \n {0}\n".format(e))
        sys.stderr.write("Please check mamonsu user permissions and rerun bootstrap.\n")
        sys.exit(2)

    if args.args.create_extensions:
        try:
            bootstrap_grant_extension_queries = fill_grant_params(GrantsOnExtensionSchemaSQL, args)
            Pooler.query(bootstrap_grant_extension_queries)

        except Exception as e:
            sys.stderr.write("Bootstrap failed to grant execution permission to "
                             "the function which required pg_buffercache extension.\n")
            sys.stderr.write("Error: \n {0}\n".format(e))

    sys.stdout.write("Bootstrap successfully completed\n")
