# -*- coding: utf-8 -*-
import os
import threading
import logging

from mamonsu.plugins.pgsql.driver.pg8000 import connect
from mamonsu.plugins.pgsql.driver.pg8000.core import ProgrammingError


class ConnectionInfo(object):

    def __init__(self, info={}):
        self._connection_info = info
        self.host = info.get('host') or os.environ.get('PGHOST')
        self.port = info.get('port') or int(os.environ.get('PGPORT') or 5432)
        self.user = info.get('user') or os.environ.get('PGUSER')
        self.passwd = info.get('passwd') or os.environ.get('PGPASSWORD')
        self.db = info.get('db') or os.environ.get('PGDATABASE')
        self.timeout = info.get('timeout') or int(
            os.environ.get('PGTIMEOUT') or 1)
        self.appname = info.get('appname') or os.environ.get('PGAPPNAME')
        self.log = logging.getLogger('PGSQL-({0})'.format(self.conn_str()))

    def conn_str(self):
        return 'host={0} db={1} user={2} port={3}'.format(
            self.host, self.db, self.user, self.port)


class Connection(ConnectionInfo):

    def __init__(self, info={}):
        super(Connection, self).__init__()
        self.lock = threading.Lock()
        self.conn = None
        self.connected = False

    def query(self, query):
        self.lock.acquire()
        try:
            self.log.debug('Run: "{0}"'.format(query))
            self._check_connect()
            self.connected = False
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            self.connected = True
        except ProgrammingError as e:
            error_text = '{0}'.format(e)
            if error_text == 'no result set':
                return None
            else:
                raise ProgrammingError(error_text)
        finally:
            self.lock.release()
        return result

    def _close(self):
        if self.conn is not None:
            self.log.debug('closing old connection')
            try:
                self.conn.close()
            except Exception as e:
                self.log.error('close error: {0}'.format(e))

    def _connect(self):
        self.log.debug('connecting')
        host, unix_sock = self.host, None
        if host.startswith('/'):
            unix_sock, host = host, None
        self.conn = connect(
            user=self.user,
            password=self.passwd,
            unix_sock=unix_sock,
            host=host,
            port=self.port,
            database=self.db,
            application_name=self.appname
        )
        self.log.debug('connected')
        self.conn.autocommit = True
        cur = self.conn.cursor()
        cur.execute('set statement_timeout to {0}'.format(self.timeout * 1000))
        cur.close()
        self.log.debug('ready')

    def _check_connect(self):
        if not self.connected:
            self.log.debug('reconnecting')
            self._close()
            self._connect()
