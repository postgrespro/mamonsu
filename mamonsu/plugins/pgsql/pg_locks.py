# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgLocks(Plugin):
    #query = """select lower(mode), count(mode) FROM pg_catalog.pg_locks group by 1 """
    query = """select count(mode) FROM pg_catalog.pg_locks"""
    Items = [
        # key, desc, color
        ('accessshare',
            'Read only queries',
            '0000CC') ]



    def run(self, zbx):
        result = Pooler.query(self.query)
        for item in self.Items:
            found = False
            for row in result:
                if row[0] == '{0}lock'.format(item[0]):
                    found = True
                    zbx.send('pgsql.pg_locks[{0}]'.format(item[0]), row[1])
            if not found:
                zbx.send('pgsql.pg_locks[{0}]'.format(item[0]), 0)

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

    def keys_and_queries(self, template_zabbix):
        result = ''
        for item in self.Items:
            result +=\
            template_zabbix.key_and_query({'UserParameter=pgsql.pg_locks[{0}],/opt/pgpro/std-10/bin/psql -qAt -p 5433 -U postgres -d postgres -c "{1}"'.format(item[0],
                                                                                                        self.query)})
            result += '\n'
        return result

