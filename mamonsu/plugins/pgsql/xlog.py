# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Xlog(Plugin):

    DEFAULT_CONFIG = {'lag_more_then_in_sec': str(60 * 5)}
    query_wal_lsn_diff = " select pg_catalog.pg_wal_lsn_diff " \
                         "(pg_catalog.pg_current_wal_lsn(), '0/00000000')"
    key_wall = 'pgsql.wal.write[]'
    key_count_wall = "pgsql.wal.count[]"
    AgentPluginType = 'pg'

    def run(self, zbx):

        if Pooler.in_recovery():
            # replication lag
            lag = Pooler.run_sql_type('replication_lag_slave_query')
            if lag[0][0] is not None:
                zbx.send('pgsql.replication_lag[sec]', float(lag[0][0]))
        else:
            Pooler.run_sql_type('replication_lag_master_query')
            # xlog location
            if Pooler.server_version_greater('10.0'):
                result = Pooler.query(self.query_wal_lsn_diff)
            else:
                result = Pooler.query("""
                    select pg_catalog.pg_xlog_location_diff
                    (pg_catalog.pg_current_xlog_location(), '0/00000000')""")
            zbx.send(self.key_wall, float(result[0][0]), self.DELTA_SPEED)
        # count of xlog files
        if Pooler.server_version_greater('10.0'):
            result = Pooler.run_sql_type('count_wal_files')
        else:
            result = Pooler.run_sql_type('count_xlog_files')
        zbx.send(self.key_count_wall, int(result[0][0]))

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL: streaming replication lag',
            'key': 'pgsql.replication_lag[sec]'
        }) + template.item({
            'name': 'PostgreSQL: wal write speed',
            'key': self.key_wall,
            'units': Plugin.UNITS.bytes
        }) + template.item({
            'name': 'PostgreSQL: count of xlog files',
            'key': self.key_count_wall
        })

    def graphs(self, template):
        result = template.graph({
            'name': 'PostgreSQL write-ahead log generation speed',
            'items': [
                {'color': 'CC0000',
                    'key': self.key_wall}]})
        result += template.graph({
            'name': 'PostgreSQL replication lag in second',
            'items': [
                {'color': 'CC0000',
                    'key': 'pgsql.replication_lag[sec]'}]})
        result += template.graph({
            'name': 'PostgreSQL count of xlog files',
            'items': [
                {'color': 'CC0000',
                    'key': self.key_count_wall}]})
        return result

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL streaming lag to high '
            'on {HOSTNAME} (value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.replication_lag[sec].last'
            '()}&gt;' + self.plugin_config('lag_more_then_in_sec')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('{0},"{1}"'.format(self.key_count_wall, Pooler.SQL['count_wal_files'][0]))
        result.append('{0},"{1}"'.format(self.key_wall, self.query_wal_lsn_diff))
        # FIXME for diff types of PG
        return template_zabbix.key_and_query(result)
