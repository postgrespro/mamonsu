# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgBufferCache(Plugin):

    Items = [
        # key, name, color
        ('size', 'PostgreSQL: shared buffer size', '0000CC'),
        ('twice_used', 'PostgreSQL: shared buffer twice used size', 'CC0000'),
        ('dirty', 'PostgreSQL: shared buffer dirty size', '00CC00')
    ]

    def run(self, zbx):
        if not self.extension_installed('pg_buffercache'):
            return
        result = Pooler.run_sql_type('buffer_cache')[0]
        for i, value in enumerate(result):
            zbx.send('pgsql.buffers[{0}]'.format(self.Items[i][0]), value)

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': 'pgsql.buffers[{0}]'.format(item[0]),
                'name': item[1],
                'units': Plugin.UNITS.bytes
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            items.append({
                'key': 'pgsql.buffers[{0}]'.format(item[0]),
                'color': item[2]})
        return template.graph({
            'name': 'PostgreSQL: shared buffer',
            'items': items})
