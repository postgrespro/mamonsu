# -*- coding: utf-8 -*-

import logging
from mamonsu.plugins.pgsql.pool import Pooler


class PostgresInfo(object):

    QueryPgSettings = """
                select
                    name,
                    setting,
                    unit,
                    context,
                    vartype,
                    source,
                    boot_val,
                    reset_val
                from pg_catalog.pg_settings
            """

    def __init__(self, args):
        self.args = args

    def run(self):
        self.settings = self._fetch_settings()

    def _fetch_settings(self):
        result = {}
        try:
            for row in Pooler.query(self.QueryPgSettings):
                result[row[0]] = {}
        except Exception as e:
            logging.error("QueryPgSettings error: {0}".format(e))
            return result
