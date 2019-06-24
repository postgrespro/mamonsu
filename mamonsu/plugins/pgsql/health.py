# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
import time


class PgHealth(Plugin):
    AgentPluginType = 'pg'
    DEFAULT_CONFIG = {'uptime': str(60 * 10), 'cache': str(80)}
    query_health = "select 1 as health;"
    query_uptime = "select date_part('epoch', now() - pg_postmaster_start_time());"
    query_cache = "select " \
                  "round(sum(blks_hit)*100/sum(blks_hit+blks_read), 2)" \
                  "from pg_catalog.pg_stat_database;"
    key_ping = "pgsql.ping{0}"
    key_uptime = "pgsql.uptime{0}"
    key_cache = "pgsql.cache{0}"

    def run(self, zbx):

        start_time = time.time()
        Pooler.query(self.query_health)
        zbx.send(self.key_ping.format('[]'), (time.time() - start_time) * 100)  # FIXME for agent type

        result = Pooler.query(self.query_uptime)
        zbx.send(self.key_uptime.format('[]'), int(result[0][0]))

        result = Pooler.query(self.query_cache)
        zbx.send(self.key_cache.format('[hit]'), int(result[0][0]))

    def items(self, template):
        result = ''
        if self.Type == "mamonsu":
            delay = 60 #TODO check delay
            value_type = Plugin.VALUE_TYPE.numeric_unsigned
        else:
            delay = 5
            value_type = Plugin.VALUE_TYPE.numeric_float
        result += template.item({
            'name': 'PostgreSQL: ping',
            'key': self.right_type(self.key_ping),
            'value_type': Plugin.VALUE_TYPE.numeric_float,
            'units': Plugin.UNITS.ms,
            'delay': delay
        }) + template.item({
            'name': 'PostgreSQL: cache hit ratio',
            'key':  self.right_type(self.key_cache, "hit"),
            'value_type': value_type,
            'units': Plugin.UNITS.percent
        }) + template.item({
            'name': 'PostgreSQL: service uptime',
            'key': self.right_type(self.key_uptime),
            'value_type': value_type,
            'units': Plugin.UNITS.uptime
        })
        return result

    def graphs(self, template):
        items = [
            {'key': self.right_type(self.key_cache, "hit")},
            {'key': self.right_type(self.key_uptime), 'color': 'DF0101', 'yaxisside': 1}
        ]
        graph = {'name': 'PostgreSQL uptime', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        result = template.trigger({
            'name': 'PostgreSQL service was restarted on '
            '{HOSTNAME} (uptime={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:' + self.right_type(self.key_uptime) + '.last()}&lt;' +
                          str(self.plugin_config('uptime'))
        }) + template.trigger({
            'name': 'PostgreSQL cache hit ratio too low on '
            '{HOSTNAME} ({ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:' + self.right_type(self.key_cache, "hit") + '.last()}&lt;' +
                          str(self.plugin_config('cache'))
        })
        return result

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key_ping.format(''), self.query_health))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key_uptime.format(''), self.query_uptime))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key_cache.format('.hit'), self.query_cache))
        return template_zabbix.key_and_query(result)