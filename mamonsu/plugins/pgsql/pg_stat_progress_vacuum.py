from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgStatProgressVacuum(Plugin):
    DEFAULT_CONFIG = {'max_index_vacuum_count': str(1)}
    AgentPluginType = 'pg'
    query = """select count(c.relname) from pg_stat_progress_vacuum v inner join pg_class c on v.relid = c.oid"""
    key = 'pgsql.pg_stat_progress_vacuum{0}'

    def run(self, zbx):
        result = Pooler.query(self.query)
        zbx.send(self.right_type(self.key), result[0][0])

    def items(self, template):
        result = ''
        result += template.item({
            'key': self.right_type(self.key),
            'name': 'PostgreSQL vacuum count',
            'value_type': self.VALUE_TYPE.numeric_unsigned
        })
        return result

    def graphs(self, template):
        name, items = 'PostgreSQL count vacuuming tables', []
        items.append({
            'key': self.right_type(self.key),
            'color': '0000CC'
        })
        return template.graph({'name': name, 'items': items})

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL count tables where index_vacuum_count is more than 1 on {HOSTNAME}',
            'expression': '{#TEMPLATE:' + self.right_type(self.key) +
                          '.last()}&gt;' + self.plugin_config('max_index_vacuum_count')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('{0},$2 $1 -c "{1}"'.format(self.key.format('[*]'), self.query))
        return template_zabbix.key_and_query(result)

    def sql(self):
        result = {}  # key is name of file, var is query
        result[self.key.format('')] = self.query
        return result
