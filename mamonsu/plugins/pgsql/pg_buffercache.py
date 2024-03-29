# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgBufferCache(Plugin):
    AgentPluginType = "pg"
    key = "pgsql.buffers{0}"
    query_agent_size = """
    SELECT sum(1) * (current_setting('block_size')::int8) AS size
    FROM {0}.pg_buffercache;
    """
    query_agent_twice_used = """
    SELECT sum(CASE WHEN usagecount > 1 THEN 1 ELSE 0 END) * (current_setting('block_size')::int8) AS twice_used
    FROM {0}.pg_buffercache;
    """
    query_agent_dirty = """
    SELECT sum(CASE isdirty WHEN true THEN 1 ELSE 0 END) * (current_setting('block_size')::int8) AS dirty
    FROM {0}.pg_buffercache;
    """
    query = [query_agent_size, query_agent_twice_used, query_agent_dirty]
    Items = [
        # key, name, color
        ("size", "PostgreSQL pg_buffercache: Shared Buffer Size", "00CC00"),
        ("twice_used", "PostgreSQL pg_buffercache: Shared Buffer Twice Used Size", "006AAE"),
        ("dirty", "PostgreSQL pg_buffercache: Shared Buffer Dirty Size", "FF5656")
    ]

    graph_name = "PostgreSQL pg_buffercache: Shared Buffer"

    def run(self, zbx):
        if not Pooler.extension_installed("pg_buffercache"):
            self.disable_and_exit_if_extension_is_not_installed("pg_buffercache")
        result = Pooler.run_sql_type("buffer_cache", extension="pg_buffercache")[0]
        for i, value in enumerate(result):
            zbx.send("pgsql.buffers[{0}]".format(self.Items[i][0]), value)

    def items(self, template, dashboard=False):
        result = ""
        for item in self.Items:
            result += template.item({
                "key": self.right_type(self.key, item[0]),  # 'pgsql.buffers[{0}]'.format(item[0]),
                "name": item[1],
                "delay": self.plugin_config("interval"),
                "units": Plugin.UNITS.bytes
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items = []
        for item in self.Items:
            items.append({
                "key": self.right_type(self.key, item[0]),
                "color": item[2],
                "drawtype": 2})
        if not dashboard:
            return template.graph({
                "name": self.graph_name,
                "items": items})
        else:
            return []

    def keys_and_queries(self, template_zabbix):
        if Pooler.extension_installed("pg_buffercache"):
            result = []
            for i, item in enumerate(self.Items):
                result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[0]), self.query[i].format(
                    self.extension_schema(extension="pg_buffercache"))))
            return template_zabbix.key_and_query(result)
        else:
            return
