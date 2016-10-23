# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class BgWriter(Plugin):

    Items = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta

        ('buffers_checkpoint', 'bgwriter[buffers_checkpoint]',
            'bgwriter: buffers written during checkpoints',
            ('PostgreSQL bgwriter', 'CCCC00', 1),
            Plugin.UNITS.bytes, Plugin.DELTA.simple_change),

        ('buffers_clean', 'bgwriter[buffers_clean]',
            'bgwriter: buffers written',
            ('PostgreSQL bgwriter', '0000CC', 1),
            Plugin.UNITS.bytes, Plugin.DELTA.simple_change),

        ('maxwritten_clean', 'bgwriter[maxwritten_clean]',
            'bgwriter: number of bgwriter stopped by max write count',
            ('PostgreSQL bgwriter', '777777', 0),
            Plugin.UNITS.ms, Plugin.DELTA.simple_change),

        ('buffers_backend', 'bgwriter[buffers_backend]',
            'bgwriter: buffers written directly by a backend',
            ('PostgreSQL bgwriter', 'CC0000', 1),
            Plugin.UNITS.bytes, Plugin.DELTA.simple_change),

        ('buffers_backend_fsync', 'bgwriter[buffers_backend_fsync]',
            'bgwriter: times a backend execute its own fsync',
            ('PostgreSQL bgwriter', 'CC00CC', 0),
            Plugin.UNITS.none, Plugin.DELTA.simple_change),

        ('buffers_alloc', 'bgwriter[buffers_alloc]',
            'bgwriter: buffers allocated',
            ('PostgreSQL bgwriter', '00CC00', 1),
            Plugin.UNITS.bytes, Plugin.DELTA.simple_change)
    ]

    def run(self, zbx):
        params = [x[0] for x in self.Items]
        result = Pooler.query(
            'select {0} from pg_catalog.pg_stat_bgwriter'.format(
                ', '.join(params)))
        for idx, val in enumerate(result[0]):
            key, val = 'pgsql.{0}'.format(
                self.Items[idx][1]), int(val)
            zbx.send(key, val, self.Items[idx][5])
        del params, result

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': 'pgsql.{0}'.format(item[1]),
                'name': 'PostgreSQL {0}'.format(item[2]),
                'value_type': self.VALUE_TYPE.numeric_unsigned,
                'units': item[4]
            })
        return result

    def graphs(self, template):
        name = 'PostgreSQL bgwriter'
        items = []
        for item in self.Items:
            if not item[3] is None:
                if item[3][0] == name:
                    items.append({
                        'key': 'pgsql.{0}'.format(item[1]),
                        'color': item[3][1],
                        'yaxisside': item[3][2]
                    })
        return template.graph({'name': name, 'items': items})
