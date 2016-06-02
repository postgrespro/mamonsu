import os
from ._connection import Connection


class Pool(object):

    ExcludeDBs = ['template0', 'template1', 'postgres']

    def __init__(self):
        self.connections = {}

    def query(self, query, database=None):
        if database is None:
            database = os.environ.get('PGDATABASE')
        self.__install_connection(database)
        return self.connections[database].query(query)

    def is_extension_installed(self, ext, database):
        result = self.query('select count(*) from pg_catalog.pg_extension\
            where extname = "{0}"'.format(ext), database)
        return (int(result[0][0])) == 1

    def databases(self):
        result, databases = self.query('select datname from \
            pg_catalog.pg_database'), []
        for row in result:
            if row[0] not in self.ExcludeDBs:
                databases.append(row[0])
        return databases

    def __install_connection(self, database):
        conn = self.connections.get(database)
        if conn is None:
            self.connections[database] = Connection(database)

Pooler = Pool()
