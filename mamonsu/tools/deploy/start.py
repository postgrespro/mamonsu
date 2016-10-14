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


QuerySplit = """

"""

CreateSchemaSQL = """
CREATE TABLE IF NOT EXISTS public.mamonsu_config (
  version text,
  inserted_at timestamp DEFAULT NOW()
);

INSERT INTO public.mamonsu_config(version) VALUES('{0}');

DROP TABLE IF EXISTS public.mamonsu_timestamp_master_{1};

CREATE TABLE public.mamonsu_timestamp_master_{1}(
    id int primary key,
    ts double precision,
    lsn pg_lsn
);

INSERT INTO public.mamonsu_timestamp_master_{1} (id) values (1);

CREATE OR REPLACE FUNCTION public.mamonsu_timestamp_master_update()
RETURNS void AS $$
  UPDATE public.mamonsu_timestamp_master_{1} SET
    ts = extract(epoch from now() at time zone 'utc')::double precision,
    lsn = pg_catalog.pg_current_xlog_location()
  WHERE
    id = 1;
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_timestamp_get()
RETURNS double precision AS $$
  SELECT
    (extract(epoch from now() at time zone 'utc') - ts)::double precision
  FROM public.mamonsu_timestamp_master_{1}
  WHERE id = 1 LIMIT 1;
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_count_autovacuum()
RETURNS BIGINT AS $$
    SELECT
        count(*)::BIGINT
    FROM pg_catalog.pg_stat_activity
    WHERE
        query like '%%autovacuum%%'
        and state <> 'idle'
        and pid <> pg_catalog.pg_backend_pid()
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_count_xlog_files()
RETURNS BIGINT AS $$
WITH list(filename) as (SELECT * FROM pg_catalog.pg_ls_dir('pg_xlog'))
SELECT
    COUNT(*)::BIGINT
FROM
    list
WHERE filename similar to '{2}'
$$ LANGUAGE SQL SECURITY DEFINER;
""".format(
    mamonsu_version,
    mamonsu_version.replace('.', '_'), '[0-9A-F]{24}')


class Args(DefaultConfig):

    def __init__(self):
        parser = optparse.OptionParser(
            usage='%prog deploy',
            version='%prog deploy {0}'.format(mamonsu_version),
            description='Deploy DDL for monitoring')
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
                    sys.stderr.write("Can't run as postgres\n")
                    return False
            else:
                sys.stderr.write("Can't configure auto-host for postgresql\n")
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
    args.try_configure_connect_to_pg()

    try:
        for sql in CreateSchemaSQL.split(QuerySplit):
            Pooler.query(sql)
    except Exception as e:
        sys.stderr.write("Query:\n{0}\nerror: {1}\n".format(sql, e))
        sys.exit(1)
