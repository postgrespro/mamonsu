# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from mamonsu.plugins.pgsql.pool import Pooler


class BiggestTables(Plugin):

    # every 5 min
    Interval = 5*60
    # only 10 biggest tables
    Limit = 10

    def run(self, zbx):
        result = Pooler.query('select datname \
            from pg_catalog.pg_database where datistemplate = false')
        tables = []
        for db in result:
            info_sizes = Pooler.query("select n.nspname||'.'||c.relname, \
                    pg_catalog.pg_total_relation_size(c.oid) as size from \
                    pg_catalog.pg_class c left join pg_catalog.pg_namespace n \
                    ON n.oid = c.relnamespace order by size \
                    desc limit {0};".format(self.Limit), db[0])
            tables.append({'{#TABLE}': info_sizes[0]})
            zbx.send('pgsql.table.size[{0}]'.format(
                info_sizes[0]), info_sizes[1])
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
                'value_type': self.VALUE_TYPE.numeric_unsigned,
                'delay': self.Interval}]
        return template.discovery_rule(rule=rule, items=items)
