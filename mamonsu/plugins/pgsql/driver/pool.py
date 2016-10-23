import mamonsu.lib.platform as platform
from distutils.version import LooseVersion
from ._connection import Connection, ConnectionInfo


class Pool(ConnectionInfo):

    ExcludeDBs = ['template0', 'template1', 'postgres']

    SQL = {
        # query type: ( 'if_not_installed', 'if_installed' )
        'replication_lag_master_query': (
            'select 1 as replication_lag_master_query',
            'select public.mamonsu_timestamp_master_update()'
        ),
        'replication_lag_slave_query': (
            'select extract(epoch from now()-pg_last_xact_replay_timestamp())',
            'select public.mamonsu_timestamp_get()'
        ),
        'count_xlog_files': (
            "select count(*) from pg_catalog.pg_ls_dir('pg_xlog')",
            'select public.mamonsu_count_xlog_files()'
        ),
        'count_autovacuum': (
            """select count(*) from pg_catalog.pg_stat_activity where
query like '%%autovacuum%%' and state <> 'idle'
and pid <> pg_catalog.pg_backend_pid()
        """,
            'select public.mamonsu_count_autovacuum()'
        ),
        'buffer_cache': (
            """select
sum(1) * 8 * 1024 as size,
sum(case when usagecount > 1 then 1 else 0 end) * 8 * 1024 as twice_used,
sum(case isdirty when true then 1 else 0 end) * 8 * 1024 as dirty
from public.pg_buffercache""",
            'select size, twice_used, dirty from public.mamonsu_buffer_cache()'
        ),
    }

    def __init__(self):
        super(Pool, self).__init__()
        self.all_connections = {}
        self._server_version = {}
        self._mamonsu_bootstrap = {}
        self._in_recovery = {}
        self._in_recovery_cache = 0

    def connection_string(self, db=None):
        self._init_conn_(db)
        return self.all_connections[db].conn_str()

    def query(self, query, db=None):
        if db is None:
            db = self.db
        self._init_conn_(db)
        return self.all_connections[db].query(query)

    def server_version(self, db=None):
        if db in self._server_version:
            return self._server_version[db]
        if platform.PY2:
            result = self.query('show server_version', db)[0][0]
        elif platform.PY3:
            result = bytes(
                self.query('show server_version', db)[0][0], 'utf-8')
        self._server_version[db] = "{0}".format(result.decode('ascii'))
        return self._server_version[db]

    def in_recovery(self, db=None):
        if (db in self._in_recovery) and (self._in_recovery_cache < 10):
            self._in_recovery_cache += 1
            return self._server_version[db]
        self._in_recovery_cache = 0
        self._in_recovery[db] = self.query(
            "select pg_catalog.pg_is_in_recovery()")[0][0]
        return self._in_recovery[db]

    def server_version_greater(self, version, db=None):
        return self.server_version(db) >= LooseVersion(version)

    def server_version_less(self, version, db=None):
        return self.server_version(db) <= LooseVersion(version)

    def mamonsu_bootstrap(self, db=None):
        if db in self._mamonsu_bootstrap:
            return self._mamonsu_bootstrap[db]
        sql = """select count(*) from pg_catalog.pg_class
            where relname = 'mamonsu_config'"""
        result = int(self.query(sql, db)[0][0])
        self._mamonsu_bootstrap[db] = (result == 1)
        if self._mamonsu_bootstrap[db]:
            self.log.info("Detect mamonsu bootstrap")
        else:
            self.log.info("Can't detect mamonsu bootstrap")
        return self._mamonsu_bootstrap[db]

    def extension_installed(self, ext, db=None):
        result = self.query('select count(*) from pg_catalog.pg_extension\
            where extname = \'{0}\''.format(ext), db)
        return (int(result[0][0])) == 1

    def databases(self):
        result, databases = self.query('select datname from \
            pg_catalog.pg_database'), []
        for row in result:
            if row[0] not in self.ExcludeDBs:
                databases.append(row[0])
        return databases

    def get_sql(self, typ, db=None):
        if typ not in self.SQL:
            raise LookupError("Unknown SQL type: '{0}'".format(typ))
        result = self.SQL[typ]
        if self.mamonsu_bootstrap(db):
            return result[1]
        else:
            return result[0]

    def run_sql_type(self, typ, db=None):
        return self.query(self.get_sql(typ, db), db)

    def _init_conn_(self, db):
        conn = self.all_connections.get(db)
        if conn is None:
            info = self._connection_info
            info['db'] = db
            self.all_connections[db] = Connection(info)
