# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


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

    # queries for zabbix agent
    query_agent_discovery = "SELECT json_build_object ('data',json_agg(json_build_object('{#DATABASE}',d.datname)))" \
                            " FROM pg_database d WHERE NOT datistemplate AND datallowconn AND datname!='postgres';"

    key_db_discovery = "pgsql.database.discovery{0}"
    key_db_size = "pgsql.database.size{0}"
    key_db_age = "pgsql.database.max_age{0}"
    key_db_bloating_tables = "pgsql.database.bloating_tables{0}"
    key_autovacumm = "pgsql.autovacumm.count{0}"

    DEFAULT_CONFIG = {'min_rows': str(50), 'bloat_scale': str(0.2)}

    def run(self, zbx):
        result = Pooler.query('select \
            datname, pg_database_size(datname::text), age(datfrozenxid) \
            from pg_catalog.pg_database where datistemplate = false')
        dbs = []
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
        zbx.send('pgsql.database.discovery[]', zbx.json({'data': dbs}))
        del dbs, bloat_count

        result = Pooler.run_sql_type('count_autovacuum')
        zbx.send('pgsql.autovacumm.count[]', int(result[0][0]))

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL: count of autovacuum workers',
            'key': self.right_type(self.key_autovacumm),
            'delay': self.plugin_config('interval')
        })

    def discovery_rules(self, template):
        rule = {
            'name': 'Database discovery',
            'key': self.key_db_discovery.format('[{0}]'.format(self.Macros[self.Type])),
            'filter': '{#DATABASE}:.*'
        }
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
        return template.discovery_rule(rule=rule, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('{0},$2 $1 -c "{1}"'.format(self.key_autovacumm.format("[*]"), Pooler.SQL['count_autovacuum'][0]))
        result.append('{0},$2 $1 -c "{1}"'.format(self.key_db_discovery.format("[*]"), self.query_agent_discovery))
        result.append('{0},echo "{1}" | $3 $2 -v p1="$1"'.format(self.key_db_size.format("[*]"), self.query_size))
        result.append('{0},echo "{1}" | $3 $2 -v p1="$1"'.format(self.key_db_age.format("[*]"), self.query_age))
        result.append(
            '{0},$3 $2 -d "$1" -c "{1}"'.format(self.key_db_bloating_tables.format("[*]"),
                                                self.query_bloating_tables.format(self.plugin_config('bloat_scale'),
                                                                                  self.plugin_config('min_rows'))))
        return template_zabbix.key_and_query(result)
