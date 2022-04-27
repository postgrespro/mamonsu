# Mamonsu: adding custom plugins

You can extend Mamonsu with your own custom plugins, as follows:

1. Save all custom plugins in a single directory, such as */etc/mamonsu/plugins*.  
2. Make sure this directory is specified in your configuration file under the [plugins] section:
    ```editorconfig
    [plugins]
    directory = /etc/mamonsu/plugins
    ```
3. Generate a new Zabbix template to include custom plugins:
    ```shell
    mamonsu export template template.xml --add-plugins=/etc/mamonsu/plugins
    ```
4. Upload the generated template.xml to the Zabbix server as explained in sections “[Installation](../README.md#installation)" and "[Configuration](../README.md#configuration)”.

***

## How to write custom plugin

Plugins have a fixed structure:  
```python
# all possible elements are listed here, but they are optional and it is not necessary to add all of them

# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class PLUGIN_NAME(Plugin):
    # metrics collection interval in seconds
    Interval = PLUGIN INTERVAL

    # Plugin type specifies which group new metrics will belong to. Plugin type can be one of 'pgsql', 'system' or 'all:
    # 'pgsql' configures PostgreSQL metrics
    # 'system' configures system metrics
    # 'all' configures both PostgreSQL and system metrics
    AgentPluginType = 'PLUGIN TYPE'

    # queries to form sql files
    query_plugin_metric_for_sql_file = 'QUERY'
    # example:
    # query_bloating_tables = "select count(*) from pg_catalog.pg_stat_all_tables where " \
    #                         "(n_dead_tup/(n_live_tup+n_dead_tup)::float8) > {0} and " \
    #                         "(n_live_tup+n_dead_tup) > {1};"

    # queries for zabbix agent
    query_plugin_metric_for_zabbix_agent = 'QUERY'
    # example:
    # query_size = "select pg_database_size(datname::text) from pg_catalog.pg_database where" \
    #              " datistemplate = false and datname = :'p1';"

    # zabbix elements keys
    key_plugin_metric = 'KEY'
    # example:
    # key_db_bloating_tables = 'pgsql.database.bloating_tables{0}'

    # plugin options
    DEFAULT_CONFIG = {OPTIONS}
    # example:
    # DEFAULT_CONFIG = {'min_rows': str(50), 'bloat_scale': str(0.2)}

    # run(self, zbx) specifies queries execution and processing
    def run(self, zbx):
        result = Pooler.query(self.query_plugin_metric_for_sql_file)
        zbx.send(self.key_plugin_metric, int(result[0][0]))

    # ====================================================================================
    # Methods for generating Zabbix objects
    # Each method has fixed signature (self, template, dashboard),
    # where 'dashboard' parameter specifies what type of object we are going to generate:
    # False for generating template objects;
    # True for adding objects to screen.
    def items(self, template, dashboard=False):
        if not dashboard:
            result = template.item({
                'name': 'ITEM NAME',
                'key': self.right_type(self.key_plugin_metric), # right_type() generates key depending on template type - mamonsu template key or zabbix agent template key
                'delay': self.plugin_config('interval'),
                'value_type': VALUE TYPE,  # see available values in mamonsu/lib/const.py VALUE_TYPE
                'units': UNITS,  # see available values in mamonsu/lib/const.py UNITS
                'delta': DELTA  # see available values in mamonsu/lib/const.py DELTA
            })
            return result
        else:
            # to add item (as simple graph) to Zabbix screen we must define:
            # item key ('name')
            # screen name ('page')
            # graph size ('size')
            # position on screen ('position', but it's optionally - you can set 0 to avoid sorting)
            return [{'dashboard': {'name': self.right_type(self.key_autovacumm),
                                   'page': ZbxTemplate.dashboard_page_PAGE['name'], # see available values in mamonsu/lib/zbx_template.py dashboard_page_*
                                   'size': ZbxTemplate.dashboard_widget_size_SIZE, # see available values in mamonsu/lib/zbx_template.py dashboard_widget_size_*
                                   'position': N}}]

    def discovery_rules(self, template, dashboard=False):
        rule = {
            'name': 'DISCOVERY RULE NAME',
            'key': self.key_discovery_key
        }
        items = [{
            'name': 'ITEM NAME',
            'key': self.right_type(self.key_plugin_metric),
            'delay': self.plugin_config('interval'),
            'value_type': VALUE TYPE,
            'units': UNITS,
            'delta': DELTA
        }]
        graphs = [{
            'name': 'GRAPH NAME',
            'type': GRAPH TYPE,
            'items': [{
                'name': 'ITEM NAME',
                'key': self.right_type(self.key_plugin_metric),
                'delay': self.plugin_config('interval'),
                'value_type': VALUE TYPE,
                'units': UNITS,
                'delta': DELTA
            }]
        }]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs)

        def graphs(self, template, dashboard=False):
            result = template.graph({'name': 'GRAPH NAME',
                                     'items': {
                                         'name': 'ITEM NAME',
                                         'key': self.right_type(self.key_plugin_metric),
                                         'delay': self.plugin_config('interval'),
                                         'value_type': VALUE TYPE,
                                         'units': UNITS,
                                         'delta': DELTA
                                     }})
            if not dashboard:
                return result
            else:
                # to add graph to Zabbix screen we must define:
                # graph name ('name')
                # screen name ('page')
                # graph size ('size')
                # position on screen ('position', but it's optionally - you can set 0 to avoid sorting)
                return [{'dashboard': {'name': 'GRAPH NAME',
                                       'page': ZbxTemplate.dashboard_page_PAGE['name'], # see available values in mamonsu/lib/zbx_template.py dashboard_page_*
                                       'size': ZbxTemplate.dashboard_widget_size_SIZE, # see available values in mamonsu/lib/zbx_template.py dashboard_widget_size_*
                                       'position': N}}]

        def triggers(self, template, dashboard=False):
            result = template.trigger({
                'name': 'TRIGGER NAME',
                'expression': 'TRIGGER EXPRESSION'
            })

        return result

    # ====================================================================================

    # keys_and_queries(self, template_zabbix) generates parameters files for Zabbix agent (by command export zabbix-parameters)
    def keys_and_queries(self, template_zabbix):
        result = ['{0},$2 $1 -c "{1}"'.format(self.key_plugin_metric, self.query_plugin_metric_for_zabbix_agent)]
        return template_zabbix.key_and_query(result)
```

Native Mamonsu plugins are stored in [mamonsu/plugins](../mamonsu/plugins).