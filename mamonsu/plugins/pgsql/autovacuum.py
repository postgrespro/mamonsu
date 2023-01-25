# -*- coding: utf-8 -*-
from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Autovacuum(Plugin):
    AgentPluginType = "pg"
    # TODO: unify keys and remove its direct mentioning in zbx.send() functions
    key_count = "pgsql.autovacuum.count{0}"
    key_utilization = "pgsql.autovacuum.utilization{0}"
    key_utilization_avg5 = "pgsql.autovacuum.utilization.avg5{0}"
    key_utilization_avg15 = "pgsql.autovacuum.utilization.avg15{0}"
    key_utilization_avg30 = "pgsql.autovacuum.utilization.avg30{0}"

    DEFAULT_CONFIG = {
        "interval": str(60)
    }

    def run(self, zbx):
        if Pooler.server_version_greater("10.0"):
            result_count = Pooler.run_sql_type("count_autovacuum", args=["backend_type = 'autovacuum worker'"])
            result_utilization = Pooler.run_sql_type("autovacuum_utilization",
                                                     args=["backend_type = 'autovacuum worker'"])
        else:
            result_count = Pooler.run_sql_type("count_autovacuum", args=[
                "query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()"])
            result_utilization = Pooler.run_sql_type("autovacuum_utilization", args=[
                "query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()"])
        zbx.send("pgsql.autovacuum.count[]", int(result_count[0][0]))
        zbx.send("pgsql.autovacuum.utilization[]", int(result_utilization[0][0]))

    def items(self, template, dashboard=False):
        result = ""
        if not dashboard:
            result += (template.item({
                "name": "PostgreSQL Autovacuum: Count of Autovacuum Workers",
                "key": self.right_type(self.key_count),
                "delay": self.plugin_config("interval")
            }))
            result += (template.item({
                "name": "PostgreSQL Autovacuum: Utilization per {0} seconds".format(self.plugin_config("interval")),
                "key": self.right_type(self.key_utilization),
                "value_type": Plugin.VALUE_TYPE.numeric_float,
                "units": Plugin.UNITS.percent,
                "delay": self.plugin_config("interval")
            }))
            result += (template.item({
                "name": "PostgreSQL Autovacuum: Average Utilization per 5 minutes",
                "key": self.right_type(self.key_utilization_avg5),
                "value_type": Plugin.VALUE_TYPE.numeric_float,
                "units": Plugin.UNITS.percent,
                "type": Plugin.TYPE.CALCULATED,
                "params": "avg(//{item}, 5m)".format(item=self.right_type(self.key_utilization)),
                "delay": self.plugin_config("interval")
            }))
            result += (template.item({
                "name": "PostgreSQL Autovacuum: Average Utilization per 15 minutes",
                "key": self.right_type(self.key_utilization_avg15),
                "value_type": Plugin.VALUE_TYPE.numeric_float,
                "units": Plugin.UNITS.percent,
                "type": Plugin.TYPE.CALCULATED,
                "params": "avg(//{item}, 15m)".format(item=self.right_type(self.key_utilization)),
                "delay": self.plugin_config("interval")
            }))
            result += (template.item({
                "name": "PostgreSQL Autovacuum: Average Utilization per 30 minutes",
                "key": self.right_type(self.key_utilization_avg30),
                "value_type": Plugin.VALUE_TYPE.numeric_float,
                "units": Plugin.UNITS.percent,
                "type": Plugin.TYPE.CALCULATED,
                "params": "avg(//{item}, 30m)".format(item=self.right_type(self.key_utilization)),
                "delay": self.plugin_config("interval")
            }))
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        result = template.graph({
            "name": "PostgreSQL Autovacuum: Count of Autovacuum Workers",
            "items": [{
                "key": self.right_type(self.key_count),
                "color": "87C2B9",
                "drawtype": 2
            }]
        })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": "PostgreSQL Autovacuum: Count of Autovacuum Workers",
                              "page": ZbxTemplate.dashboard_page_overview["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 5}
            }]

    def keys_and_queries(self, template_zabbix):
        result = []
        if Pooler.server_version_greater("10"):
            # TODO: define another metric key because it duplicates native zabbix agents keys
            # result.append("{0},$2 $1 -c \"{1}\"".format(self.key_count.format("[*]"),
            #                                                Pooler.SQL["count_autovacuum"][0].format(
            #                                                    "backend_type = 'autovacuum worker'")))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_utilization.format("[*]"),
                                                           Pooler.SQL["autovacuum_utilization"][0].format(
                                                               "backend_type = 'autovacuum worker'")))
        else:
            # TODO: define another metric key because it duplicates native zabbix agents keys
            # result.append("{0},$2 $1 -c \"{1}\"".format(self.key_count.format("[*]"),
            #                                                Pooler.SQL["count_autovacuum"][0].format(
            #                                                    "query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()")))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_utilization.format("[*]"),
                                                           Pooler.SQL["autovacuum_utilization"][0].format(
                                                               "query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()")))
        return template_zabbix.key_and_query(result)
