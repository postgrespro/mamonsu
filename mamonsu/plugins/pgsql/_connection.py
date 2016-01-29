# -*- coding: utf-8 -*-
import os
import threading
import logging
from .pg8000 import connect


class Connection(object):

    QueryTimeout = int(os.environ.get('PGTIMEOUT') or 1)

    def __init__(self, database):
        self.database = database
        self.lock = threading.Lock()
        self.log = logging.getLogger('PGSQL')
        self.conn = None
        self.query_completed_succ = False

    def query(self, query):
        self.lock.acquire()
        try:
            self.log.debug('[db: {0}] Run: "{1}"'.format(self.database, query))
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
                '[db: {0}] Closing...'.format(
                    self.database))
            try:
                self.conn.close()
            except Exception as e:
                self.log.error(
                    '[db: {0}] Closing error: {1}'.format(
                        self.database,
                        e))

    def _check_connect(self):
        if not self.query_completed_succ:
            self.log.debug('[db: {0}] Connecting...'.format(self.database))
            self._close()
            self.conn = connect(
                user=os.environ.get('PGUSER'),
                password=os.environ.get('PGPASSWORD'),
                host=os.environ.get('PGHOST'),
                port=int(os.environ.get('PGPORT') or 5432),
                database=self.database
            )
            self.log.debug('[db: {0}] Connected!'.format(self.database))
            self.conn.autocommit = True

            self.log.debug(
                '[db: {0}] Set statement timeout...'.format(self.database))
            cur = self.conn.cursor()
            cur.execute('set statement_timeout to {0}'.format(
                self.QueryTimeout * 1000))
            cur.close()
