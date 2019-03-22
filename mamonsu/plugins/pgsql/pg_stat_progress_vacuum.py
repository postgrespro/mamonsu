from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler



class PgStatProgressVacuum(Plugin):

    DEFAULT_CONFIG = {'max_index_vacuum_count': str(0)}

    query = """select count(v.relname) from pg_stat_progress_vacuum v inner join pg_class c on v.relid = c.oid"""
    query_agent = """select count({0}) from pg_stat_progress_vacuum v inner join pg_class c on v.relid = c.oid"""
    key = 'pgsql.pg_stat_progress_vacuum'
    Items = [
        # key, desc, color
        ('index_vacuum_count',
         'index_vacuum_count of the vacuum',
         '0000CC')
    ]

    def run(self, zbx):
        result = Pooler.query(self.query)
        for item in self.Items:
           # found = False
            for row in result:
                #if row[0] == '{0}'.format(item[0]): #
                    #found = True
                    zbx.send('{0}[{1}]'.format(self.key, item[0]), row[0])
                ## if row[i] is the same as data from select send it with data (from result)
            #if not found:
              #  zbx.send('pgsql.pg_stat_progress_vacuum[{0}]'.format(item[0]), 99) # if where is no data

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': '{0}[{1}]'.format(self.key, item[0]),
                'name': 'PostgreSQL vacuum: {0}'.format(item[1]),
                'value_type': self.VALUE_TYPE.numeric_unsigned
            })
        return result

    def graphs(self, template):
        name, items = 'PostgreSQL VACUUM', []
        for item in self.Items:
            items.append({
                'key': '{0}[{1}]'.format(self.key, item[0]),
                'color': item[2]
            })
        return template.graph({'name': name, 'items': items})

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL count tables where index_vacuum_count is more than 1 on {HOSTNAME}',
            'expression': '{#TEMPLATE:pgsql.pg_stat_progress_vacuum[index_vacuum_count]'
                          '.last()}&gt;' + self.plugin_config('max_index_vacuum_count')
        })

    def keys_and_queries(self, template_zabbix):
        result = ''
        for item in self.Items:
            result +=\
                template_zabbix.key_and_query({'UserParameter={0}.{1},/opt/pgpro/std-10/bin/psql -qAt -p 5433 -U postgres -d postgres -c "{2}"'.format(self.key, item[0],
                                                                                                        self.query_agent.format(item[0]))})
            result += '\n'
        return result
