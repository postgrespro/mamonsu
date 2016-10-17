# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgStatStatement(Plugin):

    # zbx_key, sql, desc, unit, delta, (Graph, color, side)
    Items = [

        ('stat[read_bytes]',
            'sum(shared_blks_read+local_blks_read+temp_blks_read)*8*1024',
            'read bytes/s', Plugin.UNITS.bytes, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: bytes', 'BBBB00', 0)),
        ('stat[write_bytes]',
            'sum(shared_blks_written+local_blks_written'
            '+temp_blks_written)*8*1024',
            'write bytes/s', Plugin.UNITS.bytes, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: bytes', '00CC00', 0)),
        ('stat[dirty_bytes]',
            'sum(shared_blks_dirtied+local_blks_dirtied)*8*1024',
            'dirty bytes/s', Plugin.UNITS.bytes, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: bytes', '0000CC', 0)),

        ('stat[read_time]',
            'sum(blk_read_time)/float4(100)',
            'read io time', Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: spend time', '00CC00', 0)),
        ('stat[write_time]',
            'sum(blk_write_time)/float4(100)',
            'write io time', Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: spend time', '0000CC', 0)),
        ('stat[other_time]',
            'sum(total_time-blk_read_time-blk_write_time)/float4(100)',
            'other (mostly cpu) time',
            Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
            ('PostgreSQL statements: spend time', 'BBBB00', 0))
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
            ('PostgreSQL statements: bytes', None),
            ('PostgreSQL statements: spend time', 1)]
        result = ''
        for graph_item in all_graphs:
            items = []
            for item in self.Items:
                if item[5][0] == graph_item[0]:
                    items.append({
                        'key': 'pgsql.{0}'.format(item[0]),
                        'color': item[5][1],
                        'yaxisside': item[5][2]})
            # create graph
            graph = {'name': graph_item[0], 'items': items}
            if graph_item[1] is not None:
                graph['type'] = graph_item[1]
            result += template.graph(graph)
        return result
