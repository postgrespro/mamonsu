# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class PgBufferCache(Plugin):
    AgentPluginType = 'pg'
    key = 'pgsql.buffers{0}'
    query_agent_size = "select sum(1) *  (current_setting('block_size')::int8) as size from mamonsu.pg_buffercache;"
    # for zabbix
    query_agent_twice_used = "select " \
                             "sum(case when usagecount > 1 then 1 else 0 end) * (current_setting('block_size')::int8) as twice_used " \
                             "from mamonsu.pg_buffercache;"  # for zabbix
    query_agent_dirty = "select " \
                        "sum(case isdirty when true then 1 else 0 end) * (current_setting('block_size')::int8) as dirty " \
                        "from mamonsu.pg_buffercache;"  # for zabbix
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

    def items(self, template, dashboard=False):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': self.right_type(self.key, item[0]),  # 'pgsql.buffers[{0}]'.format(item[0]),
                'name': item[1],
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.bytes
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items = []
        for item in self.Items:
            items.append({
                'key': self.right_type(self.key, item[0]),
                'color': item[2]})
        if not dashboard:
            return template.graph({
                'name': 'PostgreSQL: shared buffer',
                'items': items})
        else:
            return [{'dashboard': {'name': 'PostgreSQL: shared buffer',
                                   'page': ZbxTemplate.dashboard_page_overview['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 2}}]

    def keys_and_queries(self, template_zabbix):
        result = []
        for i, item in enumerate(self.Items):
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format('.' + item[0]),
                                                         self.query[i].format(item[0])))
        return template_zabbix.key_and_query(result)
