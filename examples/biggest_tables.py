# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from mamonsu.plugins.pgsql.pool import Pooler


class BiggestTables(Plugin):

    # every 5 min
    Interval = 5 * 60
    # only 10 biggest tables
    Limit = 10

    def run(self, zbx):
        tables = []
        for info_dbs in Pooler.query('select datname \
                from pg_catalog.pg_database where datistemplate = false'):
            for info_sizes in Pooler.query("select n.nspname, c.relname, \
                    pg_catalog.pg_total_relation_size(c.oid) as size from \
                    pg_catalog.pg_class c left join pg_catalog.pg_namespace n \
                        on n.oid = c.relnamespace \
                    where c.relkind IN ('r','v','m','S','f','') \
                    order by size \
                    desc limit {0};".format(self.Limit), info_dbs[0]):
                table_name = '{0}.{1}.{2}'.format(
                    info_dbs[0], info_sizes[0], info_sizes[1])
                tables.append({'{#TABLE}': table_name})
                zbx.send('pgsql.table.size[{0}]'.format(
                    table_name), info_sizes[2])
        zbx.send('pgsql.table.discovery[]', zbx.json({'data': tables}))

    def discovery_rules(self, template):
        rule = {
            'name': 'Biggest table discovery',
            'key': 'pgsql.table.discovery[]',
            'filter': '{#TABLE}:.*'
        }
        items = [
            {'key': 'pgsql.table.size[{#TABLE}]',
                'name': 'Table {#TABLE}: size',
                'units': Plugin.UNITS.bytes,
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
                'delay': self.Interval}]
        return template.discovery_rule(rule=rule, items=items)
