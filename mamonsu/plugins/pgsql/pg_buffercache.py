# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgBufferCache(Plugin):
    AgentPluginType = 'pg'
    key = 'pgsql.buffers{0}'
    query_agent_size = "select sum(1) * 8 * 1024 as size from public.pg_buffercache;"  # for zabbix
    query_agent_twice_used = "select sum(case when usagecount > 1 then 1 else 0 end) * 8 * 1024 as twice_used " \
                             "from public.pg_buffercache;" # for zabbix
    query_agent_dirty = "select sum(case isdirty when true then 1 else 0 end) * 8 * 1024 as dirty " \
                        "from public.pg_buffercache;" # for zabbix
    query = [query_agent_size, query_agent_twice_used, query_agent_dirty]
    Items = [
        # key, name, color
        ('size', 'PostgreSQL: shared buffer size', '0000CC'),
        ('twice_used', 'PostgreSQL: shared buffer twice used size', 'CC0000'),
        ('dirty', 'PostgreSQL: shared buffer dirty size', '00CC00')
    ]

    def run(self, zbx):
        if not self.extension_installed('pg_buffercache'):
            return
        result = Pooler.run_sql_type('buffer_cache')[0]
        for i, value in enumerate(result):
            zbx.send('pgsql.buffers[{0}]'.format(self.Items[i][0]), value)

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': self.right_type(self.key, item[0]), #'pgsql.buffers[{0}]'.format(item[0]),
                'name': item[1],
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.bytes
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            items.append({
                'key': self.right_type(self.key, item[0]),
                'color': item[2]})
        return template.graph({
            'name': 'PostgreSQL: shared buffer',
            'items': items})

    def keys_and_queries(self, template_zabbix):
        result = []
        for i, item in enumerate(self.Items):
                result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format('.'+item[0]), self.query[i].format(item[0])))
        return template_zabbix.key_and_query(result)

