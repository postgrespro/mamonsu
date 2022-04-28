# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate
import re


class Archiver(Plugin):

    AgentPluginType = "pgsql"

    DEFAULT_CONFIG = {
        "max_count_files": str(2)
    }

    Interval = 60

    # if streaming replication is on, archive queue length and size will always be 0 for replicas
    items_queue = {
        "count_files_to_archive": {
            "name": "Files Need to Archive Count",
            "value_type": Plugin.VALUE_TYPE.numeric_unsigned,
            "units": Plugin.UNITS.none,
            "delta": Plugin.DELTA.as_is,
            "color": "9C8A4E",
            "drawtype": Plugin.DRAWTYPE.BOLD_LINE,
            "yaxisside": Plugin.YAXISSIDE.LEFT,
            "query": {
                "standard": """
                            WITH values AS (
                            SELECT
                            4096/(ceil(pg_settings.setting::numeric/1024/1024)) AS segment_parts_count,
                            setting::bigint AS segment_size,
                            ('x' || substring(pg_stat_archiver.last_archived_wal from 9 for 8))::bit(32)::int AS last_wal_div,
                            ('x' || substring(pg_stat_archiver.last_archived_wal from 17 for 8))::bit(32)::int AS last_wal_mod,
                            CASE WHEN pg_is_in_recovery() THEN NULL ELSE
                            ('x' || substring(pg_{1}_name(pg_current_{0}()) from 9 for 8))::bit(32)::int END AS current_wal_div,
                            CASE WHEN pg_is_in_recovery() THEN NULL ELSE
                            ('x' || substring(pg_{1}_name(pg_current_{0}()) from 17 for 8))::bit(32)::int END AS current_wal_mod
                            FROM pg_settings, pg_stat_archiver
                            WHERE pg_settings.name = 'wal_segment_size')
                            SELECT greatest(coalesce((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1, 0), 0)::bigint AS files_count
                            FROM values;
                            """,
                "bootstrap": """
                            SELECT files_count FROM mamonsu.archive_command_files();
                            """
            }
        },
        "size_files_to_archive": {
            "name": "Files Need to Archive Size",
            "value_type": Plugin.VALUE_TYPE.numeric_unsigned,
            "units": Plugin.UNITS.bytes,
            "delta": Plugin.DELTA.as_is,
            "color": "793F5D",
            "drawtype": Plugin.DRAWTYPE.BOLD_LINE,
            "yaxisside": Plugin.YAXISSIDE.RIGHT,
            "query": {
                "standard": """
                            WITH values AS (
                            SELECT
                            4096/(ceil(pg_settings.setting::numeric/1024/1024)) AS segment_parts_count,
                            setting::bigint AS segment_size,
                            ('x' || substring(pg_stat_archiver.last_archived_wal from 9 for 8))::bit(32)::int AS last_wal_div,
                            ('x' || substring(pg_stat_archiver.last_archived_wal from 17 for 8))::bit(32)::int AS last_wal_mod,
                            CASE WHEN pg_is_in_recovery() THEN NULL ELSE
                            ('x' || substring(pg_{1}_name(pg_current_{0}()) from 9 for 8))::bit(32)::int END AS current_wal_div,
                            CASE WHEN pg_is_in_recovery() THEN NULL ELSE
                            ('x' || substring(pg_{1}_name(pg_current_{0}()) from 17 for 8))::bit(32)::int END AS current_wal_mod
                            FROM pg_settings, pg_stat_archiver
                            WHERE pg_settings.name = 'wal_segment_size')
                            greatest(coalesce(((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1) * segment_size, 0), 0)::bigint AS files_size
                            FROM values;
                            """,
                "bootstrap": """
                            SELECT files_size FROM mamonsu.archive_command_files();
                            """
            }
        }
    }

    items_status = {
        "archived_files": {
            "name": "Archived Files Count (in {0} seconds)".format(Interval),
            "value_type": Plugin.VALUE_TYPE.numeric_unsigned,
            "units": Plugin.UNITS.none,
            "delta": Plugin.DELTA.simple_change,
            "color": "578159",
            "drawtype": Plugin.DRAWTYPE.BOLD_LINE,
            "yaxisside": Plugin.YAXISSIDE.LEFT,
            "query": {
                "standard": """
                            SELECT archived_count FROM pg_stat_archiver;
                            """,
                "bootstrap": """
                            SELECT archived_count FROM mamonsu.archive_stat();
                            """
            }
        },
        "failed_trying_to_archive": {
            "name": "Failed Attempts to Archive Files Count (in {0} seconds)".format(Interval),
            "value_type": Plugin.VALUE_TYPE.numeric_unsigned,
            "units": Plugin.UNITS.none,
            "delta": Plugin.DELTA.simple_change,
            "color": "E57862",
            "drawtype": Plugin.DRAWTYPE.BOLD_LINE,
            "yaxisside": Plugin.YAXISSIDE.LEFT,
            "query": {
                "standard": """
                            SELECT failed_count FROM pg_stat_archiver;
                            """,
                "bootstrap": """
                            SELECT failed_count FROM mamonsu.archive_stat();
                            """
            }
        }
    }

    plugin_graphs = {
        "queue": {
            "name": "Queue",
            "items": items_queue
        },
        "status": {
            "name": "Status",
            "items": items_status
        }
    }

    prefixes = Plugin.generate_prefixes(plugin_type=AgentPluginType, plugin_name="Archiver")

    old_archived_count = None
    old_failed_count = None

    def run(self, zbx):

        self.disable_and_exit_if_archive_mode_is_not_on()

        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater("2.3.4"):
            query_type = "bootstrap"
        else:
            query_type = "standard"

        current_archived_count = Pooler.query(self.items_status["archived_files"]["query"][query_type])[0][0]
        current_failed_count = Pooler.query(self.items_status["failed_trying_to_archive"]["query"][query_type])[0][0]
        if self.old_archived_count is not None:
            archived_count = current_archived_count - self.old_archived_count
            zbx.send("{0}[{1}]".format(self.prefixes["key_prefix"], "archived_files"), archived_count)
        if self.old_failed_count is not None:
            failed_count = current_failed_count - self.old_failed_count
            zbx.send("{0}[{1}]".format(self.prefixes["key_prefix"], "failed_trying_to_archive"), failed_count)
        self.old_archived_count = current_archived_count
        self.old_failed_count = current_failed_count

        # check the last WAL file name to avoid XXX.history, XXX.partial, etc.
        wal_exists = bool(re.search(r'^[0-9A-Z]{24}$', str(
            Pooler.query("""
                         SELECT pg_stat_archiver.last_archived_wal
                         FROM pg_stat_archiver;
                         """)[0][0])))
        if wal_exists:
            queue_length = Pooler.query(self.items_queue["count_files_to_archive"]["query"][query_type]
                                        .format("wal_lsn", "walfile") if Pooler.server_version_greater("10.0") else
                                        self.items_queue["count_files_to_archive"]["query"][query_type]
                                        .format("xlog_location", "xlogfile"))[0][0]
            queue_size = Pooler.query(self.items_queue["size_files_to_archive"]["query"][query_type]
                                      .format("wal_lsn", "walfile") if Pooler.server_version_greater("10.0") else
                                      self.items_queue["size_files_to_archive"]["query"][query_type]
                                      .format("xlog_location", "xlogfile"))[0][0]
            zbx.send("{0}[{1}]".format(self.prefixes["key_prefix"], "count_files_to_archive"), queue_length)
            zbx.send("{0}[{1}]".format(self.prefixes["key_prefix"], "size_files_to_archive"), queue_size)

    def items(self, template, dashboard=False):
        result = ""
        for item, properties in {**self.items_queue, **self.items_status}.items():
            result += template.item({
                "key": self.right_type(self.prefixes["key_prefix"] + "{0}", item),
                "name": self.prefixes["name_prefix"] + "{0}".format(properties["name"]),
                "value_type": properties["value_type"],
                "delay": self.plugin_config("interval"),
                "units": properties["units"],
                "delta": properties["delta"]
            })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.right_type(self.prefixes["key_prefix"] + "{0}", "size_files_to_archive"),
                              "page": ZbxTemplate.dashboard_page_wal["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 3}
            },
                {
                    "dashboard": {"name": self.right_type(self.prefixes["key_prefix"] + "{0}", "archived_files"),
                                  "page": ZbxTemplate.dashboard_page_wal["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 4}
                }]

    def graphs(self, template, dashboard=False):
        result = ""
        items = []
        for graph, graph_properties in self.plugin_graphs.items():
            for item, item_properties in graph_properties["items"].items():
                items.append({
                    "key": self.right_type(self.prefixes["key_prefix"] + "{0}", item),
                    "color": item_properties["color"],
                    "drawtype": item_properties["drawtype"],
                    "yaxisside": item_properties["yaxisside"]
                })
            result += template.graph({
                "name": self.prefixes["name_prefix"] + "{0}".format(graph_properties["name"]),
                "items": items
            })
            items.clear()
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.prefixes["name_prefix"] + "{0}".format(self.plugin_graphs["queue"]["name"]),
                              "page": ZbxTemplate.dashboard_page_wal["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 1}
            }]

    def triggers(self, template, dashboard=False):
        return template.trigger({
            "name": "PostgreSQL Files Need to Archive Queue on {HOSTNAME} more than 2",
            "expression": "{#TEMPLATE:" + self.right_type(self.prefixes["key_prefix"] + "{0}", "count_files_to_archive")
                          + ".last()}&gt;" + self.plugin_config("max_count_files")
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        for item, properties in self.items_queue.items():
            result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.prefixes["key_prefix"] + "." + item,
                                                           properties["query"]["standard"].format("wal_lsn", "walfile")
                                                           if LooseVersion(self.VersionPG) >= LooseVersion("10") else
                                                           properties["query"]["standard"].format("xlog_location", "xlogfile")))
        for item, properties in self.items_status.items():
            result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.prefixes["key_prefix"] + "." + item,
                                                           properties["query"]["standard"]))
        return template_zabbix.key_and_query(result)
