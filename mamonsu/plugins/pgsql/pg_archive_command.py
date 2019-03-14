from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgStatProgressVacuum(Plugin):

    DEFAULT_CONFIG = {'max_count_files': str(1)}

    Items = [
        # key, desc, color
        ('count_files',
         'count files in archive_status',
         '0000CC')
    ]

    def run(self, zbx):
        result = Pooler.query("""
              SELECT count(*) FROM pg_ls_dir('./pg_wal/archive_status')
               """)
        for item in self.Items:
            for row in result:
                zbx.send('pgsql.pg_archive_command[{0}]'.format(item[0]), row[0])

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'key': 'pgsql.pg_archive_command[{0}]'.format(item[0]),
                'name': 'PostgreSQL archive_command:'.format(item[1]),
                'value_type': self.VALUE_TYPE.numeric_unsigned
            })
        return result

    def graphs(self, template):
        name, items = 'PostgreSQL Archive Command', []
        for item in self.Items:
            items.append({
                'key': 'pgsql.pg_archive_command[{0}]'.format(item[0]),
                'color': item[2]
            })
        return template.graph({'name': name, 'items': items})

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL count files in ./archive_status on {HOSTNAME}',
            'expression': '{#TEMPLATE:pgsql.pg_archive_command[count_files]'
                          '.last()}&gt;' + self.plugin_config('max_count_files')
        })
