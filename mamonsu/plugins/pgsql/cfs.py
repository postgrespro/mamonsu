# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Cfs(Plugin):

    ratioInterval, ratioCounter = 10, 0
    timeRatioInterval = ratioInterval * 60

    DEFAULT_CONFIG = {'force_enable': str(False)}

    compressed_ratio_sql = """
select
    n.nspname || '.' || c.relname as table_name,
    cfs_compression_ratio(c.oid::regclass) as ratio,
    (pg_catalog.pg_total_relation_size(c.oid::regclass) - pg_catalog.pg_indexes_size(c.oid::regclass)) as compressed_size
from
    pg_catalog.pg_class as c
    left join pg_catalog.pg_namespace n on n.oid = c.relnamespace
where c.reltablespace in (select oid from pg_catalog.pg_tablespace where spcoptions::text ~ 'compression')
    and c.relkind IN ('r','v','m','S','f','')

union all

select
    n.nspname || '.' || c.relname as table_name,
    cfs_compression_ratio(c.oid::regclass) as ratio,
    pg_catalog.pg_total_relation_size(c.oid::regclass) as compressed_size -- pg_toast included
from
    pg_catalog.pg_class as c
    left join pg_catalog.pg_namespace n on n.oid = c.relnamespace
where c.reltablespace in (select oid from pg_catalog.pg_tablespace where spcoptions::text ~ 'compression')
    and c.relkind = 'i' and n.nspname <> 'pg_toast';
"""

    activity_sql = """
select
    cfs_gc_activity_processed_bytes(), -- written
    cfs_gc_activity_processed_pages() * 8 * 1024, -- scanned
    cfs_gc_activity_processed_files(), -- written
    cfs_gc_activity_scanned_files(); -- scanned
"""

    prev = {}

    def run(self, zbx):

        if self.plugin_config('force_enable') == 'False':
            self.disable_and_exit_if_not_pgpro_ee()

        if self.ratioCounter == self.ratioInterval:
            relations, compressed_size, non_compressed_size = [], 0, 0
            for db in Pooler.databases():
                for row in Pooler.query(self.compressed_ratio_sql, db):
                    relation_name = '{0}.{1}'.format(db, row[0])
                    relations.append({'{#COMPRESSED_RELATION}': relation_name})
                    compressed_size += row[2]
                    non_compressed_size += row[2] * row[1]
                    zbx.send('pgsql.cfs.compress_ratio[{0}]'.format(relation_name), row[1])
            zbx.send('pgsql.cfs.discovery_compressed_relations[]', zbx.json({'data': relations}))
            zbx.send('pgsql.cfs.activity[total_compress_ratio]', non_compressed_size / compressed_size)
            del(relations, compressed_size, non_compressed_size)
            self.ratioCounter = 0
        self.ratioCounter += 1

        info = Pooler.query(self.activity_sql)[0]
        zbx.send('pgsql.cfs.activity[written_bytes]', info[0], delta=self.DELTA_SPEED, only_positive_speed=True)
        zbx.send('pgsql.cfs.activity[scanned_bytes]', info[1], delta=self.DELTA_SPEED, only_positive_speed=True)

        # calculate current compress ratio
        if ('written_bytes' in self.prev) and ('scanned_bytes' in self.prev):
            if info[0] > self.prev['written_bytes'] and info[1] > self.prev['scanned_bytes']:
                val = (self.prev['scanned_bytes'] - info[1]) / ((self.prev['written_bytes'] - info[0]) * self.Interval)
                zbx.send('pgsql.cfs.activity[current_compress_ratio]', val)
        self.prev['written_bytes'] = info[0]
        self.prev['scanned_bytes'] = info[1]

        # information about files
        zbx.send('pgsql.cfs.activity[compressed_files]', info[2] * self.Interval, delta=self.DELTA_SPEED, only_positive_speed=True)
        zbx.send('pgsql.cfs.activity[scanned_files]', info[3] * self.Interval, delta=self.DELTA_SPEED, only_positive_speed=True)

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL cfs compression: written byte/s',
            'key': 'pgsql.cfs.activity[written_bytes]',
            'units': self.UNITS.bytes,
            'delay': self.Interval
        }) + template.item({
            'name': 'PostgreSQL cfs compression: scanned byte/s',
            'key': 'pgsql.cfs.activity[scanned_bytes]',
            'units': self.UNITS.bytes,
            'delay': self.Interval
        }) + template.item({
            'name': 'PostgreSQL cfs compression: compressed files',
            'key': 'pgsql.cfs.activity[compressed_files]',
            'units': self.UNITS.none,
            'delay': self.Interval
        }) + template.item({
            'name': 'PostgreSQL cfs compression: scanned files',
            'key': 'pgsql.cfs.activity[scanned_files]',
            'units': self.UNITS.none,
            'delay': self.Interval
        }) + template.item({
            'name': 'PostgreSQL cfs compression: current ratio',
            'key': 'pgsql.cfs.activity[current_compress_ratio]',
            'units': self.UNITS.none,
            'delay': self.Interval
        }) + template.item({
            'name': 'PostgreSQL cfs compression: total ratio',
            'key': 'pgsql.cfs.activity[total_compress_ratio]',
            'units': self.UNITS.none,
            'delay': self.Interval
        })

    def graphs(self, template):
        result = template.graph({
            'name': 'PostgreSQL cfs compression: current ratio',
            'items': [{
                'key': 'pgsql.cfs.activity[current_compress_ratio]',
                'color': '00CC00'
            }]
        })
        result += template.graph({
            'name': 'PostgreSQL cfs compression: compressed files',
            'items': [{
                'key': 'pgsql.cfs.activity[compressed_files]',
                'color': '00CC00'
            }]
        })
        result += template.graph({
            'name': 'PostgreSQL cfs compression: written bytes',
            'items': [{
                'key': 'pgsql.cfs.activity[written_bytes]',
                'color': '00CC00'
            }]
        })
        result += template.graph({
            'name': 'PostgreSQL cfs compression: total ratio',
            'items': [{
                'key': 'pgsql.cfs.activity[total_compress_ratio]',
                'color': '00CC00'
            }]
        })
        return result

    def discovery_rules(self, template):
        rule = {
            'name': 'Compressed relations discovery',
            'key': 'pgsql.cfs.discovery_compressed_relations[]',
            'filter': '{#COMPRESSED_RELATION}:.*'
        }
        items = [
            {'key': 'pgsql.cfs.compress_ratio[{#COMPRESSED_RELATION}]',
                'name': 'Relation {#COMPRESSED_RELATION}: compress ratio',
                'delay': self.timeRatioInterval}
        ]
        graphs = [
            {
                'name': 'Relation {#COMPRESSED_RELATION}: compress ratio',
                'delay': self.timeRatioInterval,
                'items': [
                    {'color': '00CC00',
                        'key': 'pgsql.cfs.compress_ratio[{#COMPRESSED_RELATION}]'}]
            },
        ]
        return template.discovery_rule(rule=rule, items=items, graphs=graphs)
