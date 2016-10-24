# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgLocks(Plugin):

    Items = [
        # key, desc, color
        ('accessshare',
            'Read only queries',
            '0000CC'),
        ('rowshare',
            'SELECT FOR SHARE and SELECT FOR UPDATE',
            '00CC00'),
        ('rowexclusive',
            'Write queries',
            'CC0000'),
        ('shareupdateexclusive',
            'VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY',
            'CC00CC'),
        ('share',
            'CREATE INDEX',
            '777777'),
        ('sharerowexclusive',
            'Locks from application',
            'CCCCCC'),
        ('exclusive',
            'Locks from application or some operation on system catalogs',
            'CCCC00'),
        ('accessexclusive',
            'ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX, CLUSTER, '
            'VACUUM FULL, LOCK TABLE',
            '00CCCC')
    ]

    def run(self, zbx):
        result = Pooler.query("""
            select lower(mode), count(mode) FROM pg_catalog.pg_locks group by 1
            """)
        for row in result:
            for item in self.Items:
                if row[0] == '{0}lock'.format(item[0]):
                    zbx.send('pgsql.pg_locks[{0}]'.format(item[1]), row[1])

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': 'pgsql.pg_locks[{0}]'.format(item[0]),
                'name': 'PostgreSQL locks: {0}'.format(item[1]),
                'value_type': self.VALUE_TYPE.numeric_unsigned
            })
        return result

    def graphs(self, template):
        name, items = 'PostgreSQL locks sampling', []
        for item in self.Items:
            items.append({
                'key': 'pgsql.pg_locks[{0}]'.format(item[0]),
                'color': item[2]
            })
        return template.graph({'name': name, 'items': items})
