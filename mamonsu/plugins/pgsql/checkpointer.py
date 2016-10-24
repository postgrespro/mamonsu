# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Checkpointer(Plugin):

    Interval = 60 * 5

    DEFAULT_CONFIG = {'max_checkpoints_req': '5'}

    Items = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta

        ('checkpoints_timed', 'checkpoints[checkpoints_timed]',
            'checkpoints: by timeout',
            ('PostgreSQL checkpoints', '00CC00', 0),
            Plugin.UNITS.none, Plugin.DELTA.speed_per_second),

        ('checkpoints_req', 'checkpoints[checkpoints_req]',
            'checkpoints: required',
            ('PostgreSQL checkpoints', 'CC0000', 0),
            Plugin.UNITS.none, Plugin.DELTA.speed_per_second),

        ('checkpoint_write_time', 'checkpoint[write_time]',
            'checkpoint: write time',
            ('PostgreSQL checkpoints', '0000CC', 1),
            Plugin.UNITS.ms, Plugin.DELTA.speed_per_second),

        ('checkpoint_sync_time', 'checkpoint[checkpoint_sync_time]',
            'checkpoint: sync time',
            ('PostgreSQL checkpoints', '000000', 1),
            Plugin.UNITS.ms, Plugin.DELTA.speed_per_second)
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
                'value_type': Plugin.VALUE_TYPE.numeric_float,
                'units': item[4],
                'delay': self.Interval
            })
        return result

    def graphs(self, template):
        name = 'PostgreSQL checkpoints'
        items = []
        for item in self.Items:
            if not item[3] is None:
                if item[3][0] == name:
                    items.append({
                        'key': 'pgsql.{0}'.format(item[1]),
                        'color': item[3][1],
                        'yaxisside': item[3][2],
                        'delay': self.Interval
                    })
        return template.graph({'name': name, 'items': items})

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL required checkpoints occurs to '
            'frequently on {HOSTNAME}',
            'expression': '{#TEMPLATE:pgsql.checkpoints[checkpoints_req]'
            '.last()}&gt;' + self.plugin_config('max_checkpoints_req')
        })
