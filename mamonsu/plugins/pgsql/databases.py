# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Databases(Plugin):

    Interval = 300
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
                'select count(*) from pg_catalog.pg_stat_all_tables where\
                (n_dead_tup/(n_live_tup+n_dead_tup)::float8) > {0}\
                and (n_live_tup+n_dead_tup) > {1}'.format(
                    self.plugin_config('bloat_scale'),
                    self.plugin_config('min_rows')),
                info[0])[0][0]
            zbx.send(
                'pgsql.database.bloating_tables[{0}]'.format(info[0]),
                int(bloat_count))
        zbx.send('pgsql.database.discovery[]', zbx.json({'data': dbs}))
        del dbs, bloat_count

        result = Pooler.run_sql_type('count_autovacuum')
        zbx.send('pgsql.autovacumm.count[]', int(result[0][0]) - 1)

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL: count of autovacuum workers',
            'key': 'pgsql.autovacumm.count[]',
            'delay': self.Interval
        })

    def discovery_rules(self, template):
        rule = {
            'name': 'Database discovery',
            'key': 'pgsql.database.discovery[]',
            'filter': '{#DATABASE}:.*'
        }
        items = [
            {'key': 'pgsql.database.size[{#DATABASE}]',
                'name': 'Database {#DATABASE}: size',
                'units': Plugin.UNITS.bytes,
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
                'delay': self.Interval},
            {'key': 'pgsql.database.max_age[{#DATABASE}]',
                'name': 'Max age (datfrozenxid) in: {#DATABASE}',
                'delay': self.Interval},
            {'key': 'pgsql.database.bloating_tables[{#DATABASE}]',
                'name': 'Count of bloating tables in database: {#DATABASE}',
                'delay': self.Interval}
        ]
        graphs = [
            {
                'name': 'Database: {#DATABASE} size',
                'type': 1,
                'items': [
                    {'color': '00CC00',
                        'key': 'pgsql.database.size[{#DATABASE}]'}]
            },
            {
                'name': 'Database bloating overview: {#DATABASE}',
                'items': [
                    {'color': 'CC0000',
                        'key': 'pgsql.database.bloating_tables[{#DATABASE}]'},
                    {'color': '00CC00',
                        'key': 'pgsql.autovacumm.count[]',
                        'yaxisside': 1}]
            },
            {
                'name': 'Database max age overview: {#DATABASE}',
                'items': [
                    {'color': 'CC0000',
                        'key': 'pgsql.database.max_age[{#DATABASE}]'},
                    {'color': '00CC00',
                        'key': 'pgsql.autovacumm.count[]',
                        'yaxisside': 1}]
            }
        ]
        return template.discovery_rule(rule=rule, items=items, graphs=graphs)
