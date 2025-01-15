from .connection import Connection, ConnectionInfo

try:
    from pkg_resources import packaging
except ImportError:
    import packaging.version

class Pool(object):
    ExcludeDBs = ["template0", "template1"]

    SQL = {
        # query type: ( 'if_not_installed', 'if_installed' )
        "replication_lag_master_query": (
            """
            SELECT 1 AS replication_lag_master_query;
            """,
            """
            SELECT mamonsu.timestamp_master_update();
            """
        ),
        "replication_lag_slave_query": (
            """
            SELECT CASE WHEN NOT pg_is_in_recovery() OR coalesce(pg_last_{1}(), '0/00000000') = coalesce(pg_last_{2}(), '0/00000000')
                        THEN 0
                        ELSE extract (epoch FROM now() - coalesce(pg_last_xact_replay_timestamp(), now() - INTERVAL '{0} seconds'))
                   END;
            """,
            """
            SELECT mamonsu.timestamp_get();
            """
        ),
        "count_wal_files": (
            """
            WITH list(filename) AS (SELECT * FROM pg_catalog.pg_ls_dir('pg_{0}'))
            SELECT COUNT(*)::BIGINT
            FROM list
            WHERE filename SIMILAR TO '[0-9A-F]{{24}}';
            """,
            """
            SELECT mamonsu.count_{0}_files();
            """
        ),
        "count_autovacuum": (
            """
            SELECT count(*)
            FROM pg_catalog.pg_stat_activity
            WHERE {0};
            """,
            """
            SELECT mamonsu.count_autovacuum();
            """
        ),
        "autovacuum_utilization": (
            """
            WITH count_tb AS (
                    SELECT count(*)::float AS count
                    FROM pg_catalog.pg_stat_activity
                    WHERE {0}
                    ),
            settings_tb AS (
                    SELECT setting::float
                    FROM pg_catalog.pg_settings
                    WHERE name = 'autovacuum_max_workers'
            )
            SELECT count_tb.count*100/settings_tb.setting
            FROM count_tb, settings_tb;
            """,
            """
            SELECT mamonsu.autovacuum_utilization();
            """
        ),
        "buffer_cache": (
            """
            SELECT sum(1) * (current_setting('block_size')::int8) AS size,
                   sum(CASE WHEN usagecount > 1 THEN 1 ELSE 0 END) * (current_setting('block_size')::int8) AS twice_used,
                   sum(CASE isdirty WHEN true THEN 1 ELSE 0 END) * (current_setting('block_size')::int8) AS dirty
            FROM {0}.pg_buffercache;
            """,
            """
            SELECT size,
                   twice_used,
                   dirty
            FROM mamonsu.buffer_cache();
            """
        ),
        "wal_lag_lsn": (
            """
            SELECT application_name,
                   {0}
                   coalesce((pg_{1}_{2}_diff(pg_current_{1}_{2}(), replay_lsn))::int, 0) AS total_lag
            FROM pg_stat_replication;
            """,
            """
            SELECT application_name,
                   {0}
                   total_lag
            FROM mamonsu.count_{1}_lag_lsn();
            """
        )
    }

    def __init__(self, params=None):
        if params is None:
            params = {}
        self._params = params
        self._primary_connection_hash = None
        self._connections = {}
        self._cache = {
            "server_version": {"storage": {}},
            "bootstrap": {"storage": {}, "counter": 0, "cache": 10, "version": False},
            "recovery": {"storage": {}, "counter": 0, "cache": 10},
            "extension_schema": {"pg_buffercache": {}, "pg_stat_statements": {}, "pg_wait_sampling": {}, "pgpro_stats": {}},
            "extension_versions" : {},
            "pgpro": {"storage": {}},
            "pgproee": {"storage": {}}
        }

    def connection_string(self, db=None):
        db = self._normalize_db(db)
        return self._connections[db].to_string()

    def query(self, query, db=None):
        db = self._normalize_db(db)
        self._init_connection(db)
        return self._connections[db].query(query)

    def server_version(self, db=None):
        db = self._normalize_db(db)
        if db in self._cache["server_version"]["storage"]:
            return self._cache["server_version"]["storage"][db]

        version_string = self.query("show server_version", db)[0][0]
        result = bytes(
            version_string.split(" ")[0], "utf-8")
        self._cache["server_version"]["storage"][db] = "{0}".format(
            result.decode("ascii"))
        return self._cache["server_version"]["storage"][db]

    def extension_version(self, extension, db=None):
        db = self._normalize_db(db)
        if extension in self._cache["extension_versions"] and db in self._cache["extension_versions"][extension][db]:
            return self._cache["extension_versions"][extension][db]

        version_string = self.query("select extversion from pg_catalog.pg_extension where lower(extname) = lower('{0}');".format(extension), db)[0][0]
        result = bytes(
            version_string.split(" ")[0], "utf-8")
        self._cache["extension_versions"][extension] = {}
        self._cache["extension_versions"][extension][db] = "{0}".format(
            result.decode("ascii"))
        return self._cache["extension_versions"][extension][db]

    def server_version_greater(self, version, db=None):
        db = self._normalize_db(db)
        return packaging.version.parse(self.server_version(db)) >= packaging.version.parse(version)

    def server_version_less(self, version, db=None):
        db = self._normalize_db(db)
        return packaging.version.parse(self.server_version(db)) <= packaging.version.parse(version)

    def bootstrap_version_greater(self, version):
        return packaging.version.parse(
                str(self._cache["bootstrap"]["version"])) >= packaging.version.parse(version)

    def bootstrap_version_less(self, version):
        return packaging.version.parse(
                str(self._cache["bootstrap"]["version"])) <= packaging.version.parse(version)

    def in_recovery(self, db=None):
        db = self._normalize_db(db)
        if db in self._cache["recovery"]["storage"]:
            if self._cache["recovery"]["counter"] < self._cache["recovery"]["cache"]:
                self._cache["recovery"]["counter"] += 1
                return self._cache["recovery"]["storage"][db]
        self._cache["recovery"]["counter"] = 0
        self._cache["recovery"]["storage"][db] = self.query(
            "select pg_catalog.pg_is_in_recovery()", db)[0][0]
        return self._cache["recovery"]["storage"][db]

    def is_bootstraped(self, db=None):
        db = self._normalize_db(db)
        if db in self._cache["bootstrap"]["storage"]:
            if self._cache["bootstrap"]["counter"] < self._cache["bootstrap"]["cache"]:
                self._cache["bootstrap"]["counter"] += 1
                return self._cache["bootstrap"]["storage"][db]
        self._cache["bootstrap"]["counter"] = 0
        # TODO: изменить на нормальное название, 'config' слишком общее
        sql = """
        SELECT count(*)
        FROM pg_catalog.pg_class
        WHERE relname = 'config';
        """
        result = int(self.query(sql, db)[0][0])
        self._cache["bootstrap"]["storage"][db] = (result == 1)
        if self._cache["bootstrap"]["storage"][db]:
            self._connections[db].log.info("Found mamonsu bootstrap")
            sql = """
            SELECT max(version)
            FROM mamonsu.config;
            """
            self._cache["bootstrap"]["version"] = self.query(sql, db)[0][0]
        else:
            self._connections[db].log.info("Mamonsu bootstrap is not found")
            self._connections[db].log.info(
                "hint: run `mamonsu bootstrap` if you want to run without superuser rights")
        return self._cache["bootstrap"]["storage"][db]

    def is_superuser(self, db=None):
        _ = self._normalize_db(db)
        if self.query("""
        SELECT current_setting('is_superuser');
        """)[0][0] == "on":
            return True
        else:
            return False

    def is_pgpro(self, db=None):
        db = self._normalize_db(db)
        if db in self._cache["pgpro"]:
            return self._cache["pgpro"][db]
        try:
            self.query("""
            SELECT pgpro_version();
            """)
            self._cache["pgpro"][db] = True
        except:
            self._cache["pgpro"][db] = False
        return self._cache["pgpro"][db]

    def is_pgpro_ee(self, db=None):
        db = self._normalize_db(db)
        if not self.is_pgpro(db):
            return False
        if db in self._cache["pgproee"]:
            return self._cache["pgproee"][db]
        try:
            ed = self.query("""
            SELECT pgpro_edition();
            """)[0][0]
            self._connections[db].log.info("pgpro_edition is {}".format(ed))
            self._cache["pgproee"][db] = (ed.lower() == "enterprise")
        except:
            self._connections[db].log.info("pgpro_edition() is not defined")
            self._cache["pgproee"][db] = False
        return self._cache["pgproee"][db]

    def extension_version_greater(self, extension, version, db=None):
        db = self._normalize_db(db)
        return packaging.version.parse(self.extension_version(extension, db)) >= packaging.version.parse(version)

    def extension_version_less(self, extension, version, db=None):
        db = self._normalize_db(db)
        return packaging.version.parse(self.extension_version(extension, db)) <= packaging.version.parse(version)

    def extension_installed(self, ext, db=None):
        db = self._normalize_db(db)
        result = self.query("""
        SELECT count(*)
        FROM pg_catalog.pg_extension
        WHERE lower(extname) = lower('{0}');
        """.format(ext), db)
        return (int(result[0][0])) == 1

    def extension_schema(self, extension, db=None):
        db = self._normalize_db(db)
        if db in self._cache["extension_schema"][extension]:
            return self._cache["extension_schema"][extension][db]
        try:
            self._cache["extension_schema"][extension][db] = self.query("""
            SELECT n.nspname
            FROM pg_extension e
            JOIN pg_namespace n ON e.extnamespace = n.oid
            WHERE e.extname = '{0}'
            """.format(extension), db)[0][0]
            return self._cache["extension_schema"][extension][db]
        except:
            self._connections[db].log.info("{0} is not installed".format(extension))

    def databases(self):
        result, databases = self.query("""
        SELECT datname
        FROM pg_catalog.pg_database;
        """), []
        for row in result:
            if row[0] not in self.ExcludeDBs:
                databases.append(row[0])
        return databases

    def fill_query_params(self, query, params, extension=None, db=None):
        if not params:
            params = []
        if extension:
            params.append(self.extension_schema(extension, db))
        return query.format(*params)

    def get_sql(self, typ, args=None, extension=None, db=None):
        db = self._normalize_db(db)
        if typ not in self.SQL:
            raise LookupError("Unknown SQL type: '{0}'".format(typ))
        result = self.SQL[typ]
        if self.is_bootstraped(db):
            return self.fill_query_params(result[1], args, extension, db)
        else:
            return self.fill_query_params(result[0], args, extension, db)

    def run_sql_type(self, typ, args=None, extension=None, db=None):
        return self.query(self.get_sql(typ, args, extension, db), db)

    def _normalize_db(self, db=None):
        if db is None:
            connection_hash = self._get_primary_connection_hash()
            db = connection_hash["db"]
        return db

    # cache function for get primary connection params
    def _get_primary_connection_hash(self):
        if self._primary_connection_hash is None:
            self._primary_connection_hash = ConnectionInfo(self._params).get_hash()
        return self._primary_connection_hash

    # build connection hash
    def _build_connection_hash(self, db):
        info = ConnectionInfo(self._get_primary_connection_hash()).get_hash()
        info["db"] = self._normalize_db(db)
        return info

    def _init_connection(self, db):
        db = self._normalize_db(db)
        if db not in self._connections:
            # create new connection
            self._connections[db] = Connection(self._build_connection_hash(db))

    def get_sys_param(self, param, db=None):
        if param == "":
            #  todo
            pass
        db = self._normalize_db(db)
        if self.is_bootstraped() and self.bootstrap_version_greater("2.3.4"):
            result = self.query("""
            SELECT *
            FROM mamonsu.get_sys_param('{0}');
            """.format(param))[0][0]
        else:
            result = self.query("""
            SELECT setting
            FROM pg_catalog.pg_settings
            WHERE name = '{0}';
            """.format(param), db)[0][0]
        return result
