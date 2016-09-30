# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgStatStatement(Plugin):

    # zbx_key, sql, desc, unit, delta, (Graph, color, side)
    Items = [

        ('stat[read_bytes]',
            'sum(shared_blks_read+local_blks_read+temp_blks_read)*8*1024',
            'read bytes/s', Plugin.UNITS.bytes, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: bytes', 'CC0000', 0)),
        ('stat[write_bytes]',
            'sum(shared_blks_written+local_blks_written+temp_blks_written)*8*1024',
            'write bytes/s', Plugin.UNITS.bytes, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: bytes', '00CC00', 0)),
        ('stat[dirty_bytes]',
            'sum(shared_blks_dirtied+local_blks_dirtied)*8*1024',
            'dirty bytes/s', Plugin.UNITS.bytes, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: bytes', '0000CC', 0)),

        ('stat[total_time]',
            'sum(total_time)/float4(100*60)',
            'total execution time', Plugin.UNITS.s, Plugin.DELTA.simple_change,
            ('PostgreSQL statements: total spend time', 'CC0000', 0)),
        ('stat[read_time]',
            'sum(blk_read_time)/float4(100*60)',
            'wait read time', Plugin.UNITS.s, Plugin.DELTA.simple_change,
            ('PostgreSQL statements: read/write spend time', '00CC00', 0)),
        ('stat[write_time]',
            'sum(blk_write_time)/float4(100*60)',
            'wait write time', Plugin.UNITS.s, Plugin.DELTA.simple_change,
            ('PostgreSQL statements: read/write spend time', '0000CC', 0))
    ]

    def run(self, zbx):

        if not self.extension_installed('pg_stat_statements'):
            return

        params = [x[1] for x in self.Items]
        result = Pooler.query('\
            select {0} from public.pg_stat_statements'.format(
            ', '.join(params)))
        for idx, val in enumerate(result[0]):
            key, val = 'pgsql.{0}'.format(
                self.Items[idx][0]), int(val)
            zbx.send(key, val, self.Items[idx][4])

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': 'pgsql.{0}'.format(item[0]),
                'name': 'PostgreSQL statements: {0}'.format(item[2]),
                'value_type': self.VALUE_TYPE.numeric_float,
                'units': item[3]})
        return result

    def graphs(self, template):
        all_graphs = [
            ('PostgreSQL statements: bytes', 1),
            ('PostgreSQL statements: read/write spend time', 1),
            ('PostgreSQL statements: total spend time', 1)]
        result = ''
        for graph in all_graphs:
            items = []
            for item in self.Items:
                if item[5][0] == graph[0]:
                    items.append({
                        'key': 'pgsql.{0}'.format(item[0]),
                        'color': item[5][1],
                        'yaxisside': item[5][2]})
            result += template.graph({
                'name': graph[0],
                'items': items,
                'type': graph[1]})
        return result
