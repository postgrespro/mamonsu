# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Xlog(Plugin):

    DEFAULT_CONFIG = {'lag_more_then_in_sec': str(60 * 5)}

    def run(self, zbx):
        # is in recovery?
        result = Pooler.query('select pg_catalog.pg_is_in_recovery()')
        if str(result[0][0]) == 't' or str(result[0][0]) == 'True':
            # replication lag
            lag = Pooler.run_sql_type('replication_lag_slave_query')
            if lag[0][0] is not None:
                zbx.send('pgsql.replication_lag[sec]', float(lag[0][0]))
        else:
            Pooler.run_sql_type('replication_lag_master_query')
            # xlog location
            result = Pooler.query("""
                select pg_catalog.pg_xlog_location_diff
                    (pg_catalog.pg_current_xlog_location(),'0/00000000')""")
            zbx.send(
                'pgsql.wal.write[]', float(result[0][0]), self.DELTA_SPEED)
        # count of xlog files
        result = Pooler.run_sql_type('count_xlog_files')
        zbx.send('pgsql.wal.count[]', int(result[0][0]))

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL: streaming replication lag',
            'key': 'pgsql.replication_lag[sec]'
        }) + template.item({
            'name': 'PostgreSQL: wal write speed',
            'key': 'pgsql.wal.write[]',
            'units': Plugin.UNITS.bytes
        }) + template.item({
            'name': 'PostgreSQL: count of xlog files',
            'key': 'pgsql.wal.count[]'
        })

    def graphs(self, template):
        result = template.graph({
            'name': 'PostgreSQL write-ahead log generation speed',
            'items': [
                {'color': 'CC0000',
                    'key': 'pgsql.wal.write[]'}]})
        result += template.graph({
            'name': 'PostgreSQL replication lag in second',
            'items': [
                {'color': 'CC0000',
                    'key': 'pgsql.replication_lag[sec]'}]})
        result += template.graph({
            'name': 'PostgreSQL count of xlog files',
            'items': [
                {'color': 'CC0000',
                    'key': 'pgsql.wal.count[]'}]})
        return result

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL streaming lag to high '
            'on {HOSTNAME} (value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.replication_lag[sec].last'
            '()}&gt;' + self.plugin_config('lag_more_then_in_sec')
        })
