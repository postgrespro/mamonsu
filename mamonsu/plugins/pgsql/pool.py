from ._connection import Connection, ConnectionInfo


class Pool(ConnectionInfo):

    ExcludeDBs = ['template0', 'template1', 'postgres']

    def __init__(self):
        super(Pool, self).__init__()
        self.all_connections = {}
        self._server_version = {}

    def query(self, query, db=None):
        if db is None:
            db = self.db
        self._init_conn_(db)
        return self.all_connections[db].query(query)

    def server_version(self, db=None):
        if db in self._server_version:
            return self._server_version[db]
        self._server_version[db] = self.query('show server_version', db)
        return self._server_version[db]

    def is_extension_installed(self, ext, db):
        result = self.query('select count(*) from pg_catalog.pg_extension\
            where extname = "{0}"'.format(ext), db)
        return (int(result[0][0])) == 1

    def databases(self):
        result, databases = self.query('select datname from \
            pg_catalog.pg_database'), []
        for row in result:
            if row[0] not in self.ExcludeDBs:
                databases.append(row[0])
        return databases

    def _init_conn_(self, db):
        conn = self.all_connections.get(db)
        if conn is None:
            info = self._connection_info
            info['db'] = db
            self.all_connections[db] = Connection(info)


Pooler = Pool()
