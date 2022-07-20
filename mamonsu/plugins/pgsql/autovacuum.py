# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate

class Autovacuum(Plugin):
    
    AgentPluginType = "pg"
    key = "pgsql.autovacuum.count{0}"

    def run(self, zbx):
        if Pooler.server_version_greater("10.0"):
            result = Pooler.run_sql_type("count_autovacuum", args=["backend_type = 'autovacuum worker'"])
        else:
            result = Pooler.run_sql_type("count_autovacuum", args=[
                "query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()"])
        zbx.send("pgsql.autovacuum.count[]", int(result[0][0]))
    
    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                "name": "PostgreSQL Autovacuum: Count of Autovacuum Workers",
                "key": self.right_type(self.key),
                "delay": self.plugin_config("interval")
            })
        else:
            return []
    
    def graphs(self, template, dashboard=False):
        result = template.graph({
            "name": "PostgreSQL Autovacuum: Count of Autovacuum Workers",
            "items": [{
                "key": self.right_type(self.key),
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
        if LooseVersion(self.VersionPG) >= LooseVersion("10"):
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key.format("[*]"), 
                                                        Pooler.SQL["count_autovacuum"][0].format("backend_type = 'autovacuum worker'")))
        else:
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key.format("[*]"), 
                                                        Pooler.SQL["count_autovacuum"][0].format("query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()")))
        return template_zabbix.key_and_query(result)
