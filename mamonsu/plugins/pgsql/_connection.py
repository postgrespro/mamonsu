# -*- coding: utf-8 -*-
import os
import threading
import logging
from .pg8000 import connect


class Connection(object):

    def __init__(self, database):
        self.database = database
        self.lock = threading.Lock()
        self.log = logging.getLogger('PGSQL')
        self.conn = None
        self.last_query_completed = False

    def _conn_str(self):
        db = self.database
        host = os.environ.get('PGHOST')
        return 'host={0} db={1}'.format(host, db)

    def query(self, query):
        self.lock.acquire()
        self.last_query_completed = False
        try:
            self.log.debug(
                '[{0}] Run: "{1}"'.format(
                    self._conn_str(), query))
            self._check_connect()
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            self.last_query_completed = True
        finally:
            self.lock.release()

        return result

    def _close(self):
        if self.conn is not None:
            self.log.debug('[{0}] Closing...'.format(self._conn_str()))
            try:
                self.conn.close()
            except Exception as e:
                self.log.error('[{0}] Closing error: {1}'.format(
                    self._conn_str(), e))

    def _connect(self):
        host, unix_sock = os.environ.get('PGHOST'), None
        if host.startswith('/'):
            unix_sock, host = host, None
        self.conn = connect(
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            unix_sock=unix_sock,
            host=host,
            port=int(os.environ.get('PGPORT') or 5432),
            database=self.database,
            application_name=os.environ.get('PGAPPNAME')
        )

    def _check_connect(self):
        if not self.last_query_completed:
            self.log.debug('[{0}] Connecting...'.format(
                self._conn_str()))
            self._close()
            self._connect()
            self.log.debug(
                '[{0}] Connected!'.format(self._conn_str()))
            self.conn.autocommit = True
            self.log.debug('[{0}] Set statement_timeout...'.format(
                self._conn_str()))
            query_timeout = int(os.environ.get('PGTIMEOUT') or 1)
            cur = self.conn.cursor()
            cur.execute('set statement_timeout to {0}'.format(
                query_timeout * 1000))
            cur.close()
