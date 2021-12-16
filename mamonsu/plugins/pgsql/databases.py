# -*- coding: utf-8 -*-

from distutils.version import LooseVersion
from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Databases(Plugin):
    Interval = 60 * 5
    AgentPluginType = 'pg'
    # queries to form sql files
    query_bloating_tables = "select count(*) from pg_catalog.pg_stat_all_tables where " \
                            "(n_dead_tup/(n_live_tup+n_dead_tup)::float8) > {0} and " \
                            "(n_live_tup+n_dead_tup) > {1};"
    query_size = "select pg_database_size(datname::text) from pg_catalog.pg_database where" \
                 " datistemplate = false and datname = :'p1';"
    query_age = "select age(datfrozenxid) from pg_catalog.pg_database where datistemplate = false " \
                "and datname = :'p1';"
    query_invalid_indexes = "SELECT count (*) " \
                            "FROM pg_catalog.pg_index i LEFT JOIN pg_catalog.pg_locks l " \
                            "ON (i.indexrelid = l.relation) " \
                            "WHERE NOT (i.indisvalid AND i.indisready) AND l.relation IS NULL;"

    # queries for zabbix agent
    query_agent_discovery = "SELECT json_build_object ('data',json_agg(json_build_object('{#DATABASE}',d.datname)))" \
                            " FROM pg_database d WHERE NOT datistemplate AND datallowconn AND datname!='postgres';"

    key_db_discovery = "pgsql.database.discovery{0}"
    key_db_size = "pgsql.database.size{0}"
    key_db_age = "pgsql.database.max_age{0}"
    key_db_bloating_tables = "pgsql.database.bloating_tables{0}"
    key_autovacumm = "pgsql.autovacumm.count{0}"
    key_invalid_indexes = "pgsql.database.invalid_indexes{0}"

    DEFAULT_CONFIG = {'min_rows': str(50), 'bloat_scale': str(0.2)}

    def run(self, zbx):
        result = Pooler.query('select \
            datname, pg_database_size(datname::text), age(datfrozenxid) \
            from pg_catalog.pg_database where datistemplate = false')
        dbs = []
        bloat_count = []
        for info in result:
            dbs.append({'{#DATABASE}': info[0]})
            zbx.send('pgsql.database.size[{0}]'.format(
                info[0]), int(info[1]))
            zbx.send('pgsql.database.max_age[{0}]'.format(
                info[0]), int(info[2]))
            bloat_count = Pooler.query(
                self.query_bloating_tables.format(
                    self.plugin_config('bloat_scale'),
                    self.plugin_config('min_rows')),
                info[0])[0][0]
            zbx.send(
                'pgsql.database.bloating_tables[{0}]'.format(info[0]),
                int(bloat_count))
            invalid_indexes_count = Pooler.query(
                self.query_invalid_indexes,
                info[0])[0][0]
            zbx.send(
                'pgsql.database.invalid_indexes[{0}]'.format(info[0]),
                int(invalid_indexes_count))
        zbx.send('pgsql.database.discovery[]', zbx.json({'data': dbs}))
        del dbs, bloat_count, invalid_indexes_count

        if Pooler.server_version_greater('10.0'):
            result = Pooler.run_sql_type('count_autovacuum', args=["backend_type = 'autovacuum worker'"])
        else:
            result = Pooler.run_sql_type('count_autovacuum', args=["query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()"])
        zbx.send('pgsql.autovacumm.count[]', int(result[0][0]))

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                'name': 'PostgreSQL: count of autovacuum workers',
                'key': self.right_type(self.key_autovacumm),
                'delay': self.plugin_config('interval')
            })
        else:
            return [{'dashboard': {'name': self.right_type(self.key_autovacumm),
                                   'page': ZbxTemplate.dashboard_page_overview['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 5}}]

    def discovery_rules(self, template, dashboard=False):
        rule = {
            'name': 'Database discovery',
            'key': self.key_db_discovery.format('[{0}]'.format(self.Macros[self.Type])),

        }
        if Plugin.old_zabbix:
            conditions = []
            rule['filter'] = '{#DATABASE}:.*'
        else:
            conditions = [
                {
                    'condition': [
                        {'macro': '{#DATABASE}',
                         'value': '.*',
                         'operator': 8,
                         'formulaid': 'A'}
                    ]
                }

            ]
        items = [
            {'key': self.right_type(self.key_db_size, var_discovery="{#DATABASE},"),
             'name': 'Database {#DATABASE}: size',
             'units': Plugin.UNITS.bytes,
             'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
             'delay': self.plugin_config('interval')},
            {'key': self.right_type(self.key_db_age, var_discovery="{#DATABASE},"),
             'name': 'Max age (datfrozenxid) in: {#DATABASE}',
             'delay': self.plugin_config('interval')},
            {'key': self.right_type(self.key_db_bloating_tables, var_discovery="{#DATABASE},"),
             'name': 'Count of bloating tables in database: {#DATABASE}',
             'delay': self.plugin_config('interval')},
            {'key': self.right_type(self.key_invalid_indexes, var_discovery="{#DATABASE},"),
             'name': 'Count of invalid indexes in database: {#DATABASE}',
             'delay': self.plugin_config('interval')}
        ]
        graphs = [
            {
                'name': 'Database: {#DATABASE} size',
                'type': 1,
                'items': [
                    {'color': '00CC00',
                     'key': self.right_type(self.key_db_size, var_discovery="{#DATABASE},")}]
            },
            {
                'name': 'Database bloating overview: {#DATABASE}',
                'items': [
                    {'color': 'CC0000',
                     'key': self.right_type(self.key_db_bloating_tables, var_discovery="{#DATABASE},")},
                    {'color': '00CC00',
                     'key': self.right_type(self.key_autovacumm),
                     'yaxisside': 1}]
            },
            {
                'name': 'Database max age overview: {#DATABASE}',
                'items': [
                    {'color': 'CC0000',
                     'key': self.right_type(self.key_db_age, var_discovery="{#DATABASE},")},
                    {'color': '00CC00',
                     'key': self.right_type(self.key_autovacumm),
                     'yaxisside': 1}]
            }
        ]
        triggers = [{
            'name': 'PostgreSQL invalid indexes in database '
                    '{#DATABASE} (hostname={HOSTNAME} value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.database.invalid_indexes[{#DATABASE}].last()}&gt;0'}
        ]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs, triggers=triggers)

    def keys_and_queries(self, template_zabbix):
        result = ['{0},$2 $1 -c "{1}"'.format(self.key_db_discovery.format("[*]"), self.query_agent_discovery),
                  '{0},echo "{1}" | $3 $2 -v p1="$1"'.format(self.key_db_size.format("[*]"), self.query_size),
                  '{0},echo "{1}" | $3 $2 -v p1="$1"'.format(self.key_db_age.format("[*]"), self.query_age),
                  '{0},$3 $2 -d "$1" -c "{1}"'.format(self.key_db_bloating_tables.format("[*]"),
                                                      self.query_bloating_tables.format(
                                                          self.plugin_config('bloat_scale'),
                                                          self.plugin_config('min_rows'))),
                  '{0},$3 $2 -d "$1" -c "{1}"'.format(self.key_invalid_indexes.format("[*]"),
                                                      self.query_invalid_indexes)]
        if LooseVersion(self.VersionPG) >= LooseVersion('10'):
            result.append('{0},$2 $1 -c "{1}"'.format(self.key_autovacumm.format("[*]"), Pooler.SQL['count_autovacuum'][0].format("backend_type = 'autovacuum worker'")))
        else:
            result.append('{0},$2 $1 -c "{1}"'.format(self.key_autovacumm.format("[*]"), Pooler.SQL['count_autovacuum'][0].format("query LIKE '%%autovacuum%%' AND state <> 'idle' AND pid <> pg_catalog.pg_backend_pid()")))
        return template_zabbix.key_and_query(result)
