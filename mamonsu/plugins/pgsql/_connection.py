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
        self.query_completed_succ = False

    def _conn_string(self):
        db = self.database
        host = os.environ.get('PGHOST')
        return 'host={0} db={1}'.format(host, db)

    def query(self, query):
        self.lock.acquire()
        try:
            self.log.debug(
                '[{0}] Run: "{1}"'.format(
                    self._conn_string(), query))
            self._check_connect()
            self.query_completed_succ = False
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        finally:
            self.lock.release()

        self.query_completed_succ = True
        return result

    def _close(self):
        if self.conn is not None:
            self.log.debug(
                '[{0}] Closing...'.format(
                    self._conn_string()))
            try:
                self.conn.close()
            except Exception as e:
                self.log.error(
                    '[{0}] Closing error: {1}'.format(
                        self._conn_string(), e))

    def _check_connect(self):
        if not self.query_completed_succ:
            self.log.debug(
                '[{0}] Connecting...'.format(
                    self._conn_string()))
            self._close()
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
            self.log.debug(
                '[{0}] Connected!'.format(
                    self._conn_string()))
            self.conn.autocommit = True

            self.log.debug(
                '[{0}] Set statement timeout...'.format(
                    self._conn_string()))
            query_timeout = int(os.environ.get('PGTIMEOUT') or 1)
            cur = self.conn.cursor()
            cur.execute('set statement_timeout to {0}'.format(
                query_timeout * 1000))
            cur.close()
