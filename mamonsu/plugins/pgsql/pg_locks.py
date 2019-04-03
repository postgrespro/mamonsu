# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgLocks(Plugin):
    query = """select lower(mode), count(mode) FROM pg_catalog.pg_locks group by 1 """    # for mamonsu
    query_agent = """select count(*) FROM pg_catalog.pg_locks where lower(mode)='{0}' """   # for zabbix
    AgentPluginType = 'pg'
    key = 'pgsql.pg_locks'
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
        result = Pooler.query(self.query)
        for item in self.Items:
            found = False
            for row in result:
                if row[0] == '{0}lock'.format(item[0]):
                    found = True
                    zbx.send('{0}[{1}]'.format(self.key, item[0]), row[1])
            if not found:
                zbx.send('pgsql.pg_locks[{0}]'.format(item[0]), 0)

    def items(self, template):
        result = ''
        for item in self.Items:
                result += template.item({
                 'key': '{0}[{1}]'.format(self.key, item[0]),
                 'name': 'PostgreSQL locks: {0}'.format(item[1]),
                 'value_type': self.VALUE_TYPE.numeric_unsigned
        })

        return result

    def graphs(self, template):
        name, items = 'PostgreSQL locks sampling', []
        for item in self.Items:
            items.append({
                'key': '{0}[{1}]'.format(self.key, item[0]),
                'color': item[2]
            })
        return template.graph({'name': name, 'items': items})

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
           # result +=\
           # template_zabbix.key_and_query(['{0}.{1},/opt/pgpro/std-10/bin/psql -qAt -p 5433 -U postgres -d postgres -c "{2}"'.format(self.key, item[0],
           #                                                                                             self.query_agent.format('{0}lock'.format(item[0])))])
           # result += '\n'
           result.append(['{0}.{1},"{2}"'.format(self.key, item[0], self.query_agent.format('{0}lock'.format(item[0])))])
        return template_zabbix.key_and_query(result)

