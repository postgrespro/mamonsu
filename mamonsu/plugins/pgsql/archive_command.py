from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class ArchiveCommand(Plugin):
    AgentPluginType = 'pg'
    DEFAULT_CONFIG = {'max_count_files': str(2)}
    Interval = 60

    # if streaming replication is on, archive queue length and size will always be 0 for replicas
    query_agent_count_files = """
    WITH values AS (
    SELECT
    4096/(coalesce(1, pg_settings.setting::bigint/1024/1024)) AS segment_parts_count,
    setting::bigint AS segment_size,
    ('x' || substring(pg_stat_archiver.last_archived_wal from 9 for 8))::bit(32)::int AS last_wal_div,
    ('x' || substring(pg_stat_archiver.last_archived_wal from 17 for 8))::bit(32)::int AS last_wal_mod,
    CASE WHEN pg_is_in_recovery() THEN NULL ELSE
    ('x' || substring(pg_{1}_name(pg_current_{0}()) from 9 for 8))::bit(32)::int END AS current_wal_div,
    CASE WHEN pg_is_in_recovery() THEN NULL ELSE
    ('x' || substring(pg_{1}_name(pg_current_{0}()) from 17 for 8))::bit(32)::int END AS current_wal_mod
    FROM pg_settings, pg_stat_archiver
    WHERE pg_settings.name = 'wal_segment_size')
    SELECT greatest(coalesce((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1, 0), 0) AS count_files
    FROM values;
    """
    query_agent_size_files = """
    WITH values AS (
    SELECT
    4096/(coalesce(1, pg_settings.setting::bigint/1024/1024)) AS segment_parts_count,
    setting::bigint AS segment_size,
    ('x' || substring(pg_stat_archiver.last_archived_wal from 9 for 8))::bit(32)::int AS last_wal_div,
    ('x' || substring(pg_stat_archiver.last_archived_wal from 17 for 8))::bit(32)::int AS last_wal_mod,
    CASE WHEN pg_is_in_recovery() THEN NULL ELSE
    ('x' || substring(pg_{1}_name(pg_current_{0}()) from 9 for 8))::bit(32)::int END AS current_wal_div,
    CASE WHEN pg_is_in_recovery() THEN NULL ELSE
    ('x' || substring(pg_{1}_name(pg_current_{0}()) from 17 for 8))::bit(32)::int END AS current_wal_mod
    FROM pg_settings, pg_stat_archiver
    WHERE pg_settings.name = 'wal_segment_size')
    greatest(coalesce(((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1) * segment_size, 0), 0) AS size_files
    FROM values;
    """

    query_agent_archived_count = "SELECT archived_count from pg_stat_archiver;"
    query_agent_failed_count = "SELECT failed_count from pg_stat_archiver;"
    key = 'pgsql.archive_command{0}'
    name = 'PostgreSQL archive command {0}'
    Items = [
        # key, desc, color, side, graph
        ('count_files_to_archive', 'count files in archive_status need to archive', 'FFD700', 0, 1),
        ('size_files_to_archive', 'size of files need to archive', '00FF00', 0, 0),
        ('archived_files', 'count archived files', '00F000', 0, 1),
        ('failed_trying_to_archive', 'count attempts to archive files', 'FF0000', 0, 1),
    ]
    old_archived_count = None
    old_failed_count = None

    def run(self, zbx):
        query_queue = """
            WITH values AS (
            SELECT
            4096/(coalesce(1, pg_settings.setting::bigint/1024/1024)) AS segment_parts_count,
            setting::bigint AS segment_size,
            ('x' || substring(pg_stat_archiver.last_archived_wal from 9 for 8))::bit(32)::int AS last_wal_div,
            ('x' || substring(pg_stat_archiver.last_archived_wal from 17 for 8))::bit(32)::int AS last_wal_mod,
            CASE WHEN pg_is_in_recovery() THEN NULL ELSE
            ('x' || substring(pg_{1}_name(pg_current_{0}()) from 9 for 8))::bit(32)::int END AS current_wal_div,
            CASE WHEN pg_is_in_recovery() THEN NULL ELSE
            ('x' || substring(pg_{1}_name(pg_current_{0}()) from 17 for 8))::bit(32)::int END AS current_wal_mod
            FROM pg_settings, pg_stat_archiver
            WHERE pg_settings.name = 'wal_segment_size')
            SELECT greatest(coalesce((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1, 0), 0) AS count_files,
            greatest(coalesce(((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1) * segment_size, 0), 0) AS size_files
            FROM values;
            """

        self.disable_and_exit_if_archive_mode_is_not_on()
        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater('2.3.4'):
            result2 = Pooler.query("""SELECT * from mamonsu.archive_stat()""")
            result1 = Pooler.query("""select * from mamonsu.archive_command_files()""")
        else:
            if Pooler.server_version_greater('10.0'):
                result1 = Pooler.query(query_queue.format('wal_lsn', 'walfile'))
            else:
                result1 = Pooler.query(query_queue.format('xlog_location', 'xlogfile'))
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

    def items(self, template, dashboard=False):
        result = ''
        result += template.item({
            'key': self.right_type(self.key, self.Items[0][0]),
            'name': self.name.format(self.Items[0][1]),
            'value_type': self.VALUE_TYPE.numeric_unsigned,
            'delay': self.plugin_config('interval'),
            'delta': Plugin.DELTA.as_is
        }) + template.item({
            'key': self.right_type(self.key, self.Items[1][0]),
            'name': self.name.format(self.Items[1][1]),
            'value_type': self.VALUE_TYPE.numeric_unsigned,
            'units': self.UNITS.bytes,
            'delay': self.plugin_config('interval'),
            'delta': Plugin.DELTA.as_is
        }) + template.item({
            'key': self.right_type(self.key, self.Items[2][0]),
            'name': self.name.format(self.Items[2][1]),
            'value_type': self.VALUE_TYPE.numeric_unsigned,
            'delay': self.plugin_config('interval'),
            'delta': Plugin.DELTA.simple_change
        }) + template.item({
            'key': self.right_type(self.key, self.Items[3][0]),
            'name': self.name.format(self.Items[3][1]),
            'value_type': self.VALUE_TYPE.numeric_unsigned,
            'delay': self.plugin_config('interval'),
            'delta': Plugin.DELTA.simple_change
        })
        if not dashboard:
            return result
        else:
            return [{'dashboard': {'name': self.right_type(self.key, self.Items[1][0]),
                                   'page': ZbxTemplate.dashboard_page_wal['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 3}},
                    {'dashboard': {'name': self.right_type(self.key, self.Items[2][0]),
                                   'page': ZbxTemplate.dashboard_page_wal['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 4}}]

    def graphs(self, template, dashboard=False):
        graph = []
        result = ''
        for item in self.Items:
            if item[4] == 1:
                graph.append({
                    'key': self.right_type(self.key, item[0]), 'color': item[2], 'yaxisside': item[3]
                })
        result += template.graph({'name': self.name.format("") + ' archive status ', 'items': graph})
        if not dashboard:
            return result
        else:
            return [{'dashboard': {'name': self.name.format("") + ' archive status ',
                                   'page': ZbxTemplate.dashboard_page_wal['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 1}}]

    def triggers(self, template, dashboard=False):
        return template.trigger({
            'name': 'PostgreSQL count files in ./archive_status on {HOSTNAME} more than 2',
            'expression': '{#TEMPLATE:' + self.right_type(self.key, self.Items[0][0]) +
                          '.last()}&gt;' + self.plugin_config('max_count_files')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        if LooseVersion(self.VersionPG) >= LooseVersion('10'):
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[0][0]),
                                                         self.query_agent_count_files.format('wal_lsn', 'walfile')))
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[1][0]),
                                                         self.query_agent_size_files.format('wal_lsn', 'walfile')))
        else:
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[0][0]),
                                                         self.query_agent_count_files.format('xlog_location', 'xlogfile')))
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[1][0]),
                                                         self.query_agent_size_files.format('xlog_location', 'xlogfile')))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[2][0]),
                                                     self.query_agent_archived_count))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + self.Items[3][0]),
                                                     self.query_agent_failed_count))
        return template_zabbix.key_and_query(result)
