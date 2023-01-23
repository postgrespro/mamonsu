# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
import time
from mamonsu.lib.zbx_template import ZbxTemplate
from mamonsu.plugins.pgsql.instance import Instance


class PgHealth(Plugin):
    AgentPluginType = "pg"
    # key: (macro, value)
    plugin_macros = {
        "pg_uptime": [("macro", "{$PG_UPTIME}"), ("value", 60 * 10)],
        "cache_hit_ratio_percent": [("macro", "{$CACHE_HIT_RATIO_PERCENT}"), ("value", 80)]
    }
    query_health = """
    SELECT 1 AS health;
    """
    query_uptime = """
    SELECT ceil(extract(epoch FROM pg_postmaster_start_time()));
    """
    query_version = """
    SELECT div(setting::int, 10000) || '.' || mod(setting::int, 10000)
    FROM pg_catalog.pg_settings WHERE name = 'server_version_num';
    """

    key_ping = "pgsql.ping{0}"
    key_uptime = "pgsql.uptime{0}"
    key_cache = "pgsql.cache{0}"
    key_version = "pgsql.version{0}"

    def run(self, zbx):
        start_time = time.time()
        Pooler.query(self.query_health)
        zbx.send(self.key_ping.format("[]"), (time.time() - start_time) * 1000)
        result = Pooler.query(self.query_uptime)
        zbx.send(self.key_uptime.format("[]"), int(result[0][0]))
        result = Pooler.query(self.query_version)
        zbx.send(self.key_version.format("[]"), result[0][0])

    def items(self, template, dashboard=False):
        result = ""
        if self.Type == "mamonsu":
            delay = self.plugin_config("interval")
            value_type = Plugin.VALUE_TYPE.numeric_unsigned
        else:
            delay = 5  # TODO check delay
            value_type = Plugin.VALUE_TYPE.numeric_float
        result += template.item({
            "name": "PostgreSQL Health: Ping",
            "key": self.right_type(self.key_ping),
            "value_type": Plugin.VALUE_TYPE.numeric_float,
            "units": Plugin.UNITS.ms,
            "delay": delay
        }) + template.item({
            "name": "PostgreSQL Health: Cache Hit Ratio",
            "key": self.right_type(self.key_cache, "hit"),
            "value_type": Plugin.VALUE_TYPE.numeric_float,
            "units": Plugin.UNITS.percent,
            "type": Plugin.TYPE.CALCULATED,
            "params": "last({blocks_hit})*100/(last({blocks_hit})+last({blocks_read}))".format(
                blocks_hit=Instance.key + Instance.Items[2][1],
                blocks_read=Instance.key + Instance.Items[3][1])
        }) + template.item({
            "name": "PostgreSQL Health: Service Uptime",
            "key": self.right_type(self.key_uptime),
            "value_type": value_type,
            "delay": delay,
            "units": Plugin.UNITS.unixtime
        }) + template.item({
            "name": "PostgreSQL Health: Server Version",
            "key": self.right_type(self.key_version),
            "value_type": Plugin.VALUE_TYPE.text,
            "delay": delay,
            "units": Plugin.UNITS.none
        })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.right_type(self.key_ping),
                              "page": ZbxTemplate.dashboard_page_instance["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 1}
            },
                {
                    "dashboard": {"name": self.right_type(self.key_uptime),
                                  "page": ZbxTemplate.dashboard_page_instance["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 2}
                },
                {
                    "dashboard": {"name": self.right_type(self.key_cache, "hit"),
                                  "page": ZbxTemplate.dashboard_page_instance["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 3}
                }]

    def macros(self, template, dashboard=False):
        result = ""
        for macro in self.plugin_macros.keys():
            result += template.mamonsu_macro(defaults=self.plugin_macros[macro])
        if not dashboard:
            return result
        else:
            return []

    def triggers(self, template, dashboard=False):
        result = template.trigger({
            "name": "PostgreSQL Health: service has been restarted on {HOSTNAME} (uptime={ITEM.LASTVALUE})",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_uptime) + ".change()}&gt;" +
                          self.plugin_macros["pg_uptime"][0][1]
        }) + template.trigger({
            "name": "PostgreSQL Health: cache hit ratio too low on {HOSTNAME} ({ITEM.LASTVALUE})",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_cache, "hit") + ".last()}&lt;" +
                          self.plugin_macros["cache_hit_ratio_percent"][0][1]
        }) + template.trigger({
            "name": "PostgreSQL Health: no ping from PostgreSQL for 3 minutes on {HOSTNAME}",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_ping) + ".nodata(180)}=1"
        })
        return result

    def keys_and_queries(self, template_zabbix):
        result = ["{0}[*],$2 $1 -Aqtc \"{1}\"".format(self.key_ping.format(""), self.query_health),
                  "{0}[*],$2 $1 -Aqtc \"{1}\"".format(self.key_uptime.format(""), self.query_uptime),
                  "{0}[*],$2 $1 -Aqtc \"{1}\"".format(self.key_version.format(""), self.query_version)]
        return template_zabbix.key_and_query(result)
