# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler


class Xlog(Plugin):
    DEFAULT_CONFIG = {'lag_more_then_in_sec': str(60 * 5)}
    query_wal_lsn_diff = " select pg_catalog.pg_wal_lsn_diff " \
                         "(pg_catalog.pg_current_wal_lsn(), '0/00000000');"
    query_xlog_lsn_diff = "select pg_catalog.pg_xlog_location_diff " \
                          "(pg_catalog.pg_current_xlog_location(), '0/00000000');"
    key_wall = 'pgsql.wal.write{0}'
    key_count_wall = "pgsql.wal.count{0}"
    key_replication = "pgsql.replication_lag{0}"
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
                result = Pooler.query(self.query_xlog_lsn_diff)
            zbx.send(self.key_wall.format("[]"), float(result[0][0]), self.DELTA_SPEED)
        # count of xlog files
        if Pooler.server_version_greater('10.0'):
            result = Pooler.run_sql_type('count_wal_files')
        else:
            result = Pooler.run_sql_type('count_xlog_files')
        zbx.send(self.key_count_wall.format("[]"), int(result[0][0]))

    def items(self, template):
        result = ''
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA_SPEED
        result += template.item({
            'name': 'PostgreSQL: wal write speed',
            'key': self.right_type(self.key_wall),
            'units': Plugin.UNITS.bytes,
            'delay': self.plugin_config('interval'),
            'delta': delta
        }) + template.item({
            'name': 'PostgreSQL: streaming replication lag',
            'key': self.right_type(self.key_replication, "sec"),
            'delay': self.plugin_config('interval')
        }) + template.item({
            'name': 'PostgreSQL: count of xlog files',
            'key': self.right_type(self.key_count_wall),
            'delay': self.plugin_config('interval')
        })
        return result

    def graphs(self, template):
        result = template.graph({
            'name': 'PostgreSQL write-ahead log generation speed',
            'items': [
                {'color': 'CC0000',
                 'key': self.right_type(self.key_wall)}]})
        result += template.graph({
            'name': 'PostgreSQL replication lag in second',
            'items': [
                {'color': 'CC0000',
                 'key': self.right_type(self.key_replication, "sec")}]})
        result += template.graph({
            'name': 'PostgreSQL count of xlog files',
            'items': [
                {'color': 'CC0000',
                 'key': self.right_type(self.key_count_wall)}]})
        return result

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL streaming lag to high '
                    'on {HOSTNAME} (value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:' + self.right_type(self.key_replication, "sec") + '.last()}&gt;' +
            self.plugin_config('lag_more_then_in_sec')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        if self.VersionPG['number'] < LooseVersion('10'):
            result.append(
                '{0},$2 $1 -c "{1}"'.format(self.key_count_wall.format('[*]'), Pooler.SQL['count_xlog_files'][0]))
            result.append('{0},$2 $1 -c "{1}"'.format(self.key_wall.format('[*]'), self.query_xlog_lsn_diff))
        else:
            result.append(
                '{0},$2 $1 -c "{1}"'.format(self.key_count_wall.format('[*]'), Pooler.SQL['count_wal_files'][0]))
            result.append('{0},$2 $1 -c "{1}"'.format(self.key_wall.format('[*]'), self.query_wal_lsn_diff))
        # FIXME for lag
        result.append(
            '{0},$2 $1 -c "{1}"'.format("pgsql.replication_lag.sec[*]", Pooler.SQL['replication_lag_slave_query'][0]))
        return template_zabbix.key_and_query(result)
