from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class ArchiveCommand(Plugin):
    AgentPluginType = 'pg'
    DEFAULT_CONFIG = {'max_count_files': str(2)}
    Interval = 60
    query_agent_count_files = "SELECT count(name) AS count_files FROM (SELECT name FROM " \
                              "pg_ls_dir('./pg_{0}/archive_status') name WHERE right( name,6)= '.ready'  ) ready;"
    query_agent_size_files = "SELECT coalesce(sum((pg_stat_file('./pg_{0}/' ||  rtrim(ready.name,'.ready'))).size),0) " \
                             "AS size_files FROM (SELECT name FROM pg_ls_dir('./pg_{0}/archive_status') name " \
                             "WHERE right( name,6)= '.ready'  ) ready;"

    query_agent_archived_count = "SELECT archived_count from pg_stat_archiver;"
    query_agent_failed_count = "SELECT failed_count from pg_stat_archiver;"
    key = 'pgsql.archive_command{0}'
    name = 'PostgreSQL archive command {0}'
    Items = [
        # key, desc, color, side, graph
        ('count_files_to_archive', 'count files in archive_status need to archive', 'FF0000', 0, 0),
        ('size_files_to_archive', 'size of files need to archive', '00FF00', 1, 0),
        ('archived_files', 'count archived files', '00F000', 0, 1),
        ('failed_trying_to_archive', 'count attempts to archive files', 'FF0000', 1, 1),
    ]
    old_archived_count = None
    old_failed_count = None

    def run(self, zbx):
        self.disable_and_exit_if_archive_mode_is_not_on()
        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater('2.3.4'):
            result1 = Pooler.query("""select * from mamonsu_archive_command_files()""")
            result2 = Pooler.query("""SELECT * from mamonsu_archive_stat()""")
        else:
            if Pooler.server_version_greater('10.0'):
                xlog = 'wal'
            else:
                xlog = 'xlog'
            result1 = Pooler.query("""
            SELECT count(name) AS count_files ,
                   coalesce(sum((pg_stat_file('./pg_{0}/' ||  rtrim(ready.name,'.ready'))).size),0) AS size_files
              FROM (SELECT name FROM pg_ls_dir('./pg_{0}/archive_status') name WHERE right( name,6)= '.ready'  ) ready;
                        """.format(xlog))
            result2 = Pooler.query("""SELECT archived_count, failed_count from pg_stat_archiver;""")

        current_archived_count = result2[0][0]
        current_failed_count = result2[0][1]

        if self.old_archived_count is not None:
            archived_count = current_archived_count - self.old_archived_count
            zbx.send('pgsql.archive_command[{0}]'.format(self.Items[2][0]), archived_count)

        if self.old_failed_count is not None:
            failed_count = current_failed_count - self.old_failed_count
            zbx.send('pgsql.archive_command[{0}]'.format(self.Items[3][0]), failed_count)

        self.old_archived_count = current_archived_count
        self.old_failed_count = current_failed_count

        zbx.send('pgsql.archive_command[{0}]'.format(self.Items[0][0]), result1[0][0])
        zbx.send('pgsql.archive_command[{0}]'.format(self.Items[1][0]), result1[0][1])

    def items(self, template):
        result = ''
        for idx, item in enumerate(self.Items):
            if self.Type == "mamonsu" or idx < 2:
                delta = Plugin.DELTA.as_is
            else:
                delta = Plugin.DELTA.speed_per_second
                # TODO check if delta is right for this item
            result += template.item({
                        'key': self.right_type(self.key, item[0]),
                        'name': self.name.format(item[1]),
                        'value_type': self.VALUE_TYPE.numeric_unsigned,
                        'delta': delta
                    })
        return result

    def graphs(self, template):
        graph0 = []
        graph1 = []
        result = ''
        for item in self.Items:
            if item[4] == 0:
                graph0.append({
                    'key': self.right_type(self.key, item[0]), 'color': item[2], 'yaxisside': item[3]
                })
            if item[4] == 1:
                graph1.append({
                    'key': self.right_type(self.key, item[0]), 'color': item[2], 'yaxisside': item[3]
                })
        result += template.graph({'name': self.name.format("") + ' archive_status ', 'items': graph0})
        result += template.graph({'name': self.name.format("") + ' trying_to_archive ', 'items': graph1})
        return result

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL count files in ./archive_status on {HOSTNAME} more than 2',
            'expression': '{#TEMPLATE:' + self.right_type(self.key, self.Items[0][0]) +
                          '.last()}&gt;' + self.plugin_config('max_count_files')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        if self.VersionPG < 10.0:
            xlog = 'xlog'
        else:
            xlog = 'wal'
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[0][0]),
                                                     self.query_agent_count_files.format(xlog)))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[1][0]),
                                                     self.query_agent_size_files.format(xlog)))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[2][0]),
                                                     self.query_agent_archived_count))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[3][0]),
                                                     self.query_agent_failed_count))
        return template_zabbix.key_and_query(result)

    def sql(self):
        result = {}  # key is name of file, var is query
        if self.VersionPG < 10.0:
            xlog = 'xlog'
        else:
            xlog = 'wal'
        result[self.key.format("." + self.Items[0][0])] = self.query_agent_count_files.format(xlog)
        result[self.key.format("." + self.Items[1][0])] = self.query_agent_size_files.format(xlog)
        result[self.key.format("." + self.Items[2][0])] = self.query_agent_archived_count
        result[self.key.format("." + self.Items[3][0])] = self.query_agent_failed_count
        return result

