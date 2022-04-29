# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate

NUMBER_NON_ACTIVE_SLOTS = 0


class Wal(Plugin):
    AgentPluginType = "pgsql"

    # get amount of WAL since '0/00000000'
    query_wal_lsn_diff = """
        SELECT pg_catalog.pg_wal_lsn_diff(pg_catalog.pg_current_wal_lsn(), '0/00000000');
        """
    query_xlog_lsn_diff = """
        SELECT pg_catalog.pg_xlog_location_diff (pg_catalog.pg_current_xlog_location(), '0/00000000');
        """

    # PG 14 pg_stat_wal
    query_wal_records = """
    SELECT wal_records FROM pg_stat_wal;
    """
    query_wal_fpi = """
    SELECT wal_fpi FROM pg_stat_wal;
    """
    query_wal_buffers_full = """
    SELECT wal_buffers_full FROM pg_stat_wal;
    """
    query_wal_write_time = """
    SELECT wal_write_time FROM pg_stat_wal;
    """
    query_wal_sync_time = """
    SELECT wal_sync_time FROM pg_stat_wal;
    """
    # keys for PG 14 and higher
    key_wal_records = "pgsql.wal.records.count{0}"
    key_wal_fpi = "pgsql.wal.fpi.count{0}"
    key_wal_buffers_full = "pgsql.wal.buffers_full"
    key_wal_write_time = "pgsql.wal.write_time"
    key_wal_sync_time = "pgsql.wal.sync_time"
    key_wal_sync_duty = "pgsql.wal.sync_duty"

    key_wall = "pgsql.wal.write{0}"
    key_count_wall = "pgsql.wal.count{0}"

    def run(self, zbx):

        # count of WAL files
        result = Pooler.run_sql_type("count_wal_files", args=["wal" if Pooler.server_version_greater("10.0") else "xlog"])
        zbx.send(self.key_count_wall.format("[]"), int(result[0][0]))

        if Pooler.server_version_greater("10"):
            result = Pooler.query(self.query_wal_lsn_diff)
            zbx.send(self.key_wall.format("[]"), float(result[0][0]), self.DELTA_SPEED)
        else:
            result = Pooler.query(self.query_xlog_lsn_diff)
            zbx.send(self.key_wall.format("[]"), float(result[0][0]), self.DELTA_SPEED)

        # PG 14 pg_stat_wal metrics
        if Pooler.server_version_greater("14"):
            result = Pooler.query("""
            SELECT wal_records FROM pg_stat_wal;
            """)
            zbx.send(self.key_wal_records.format("[]"), int(result[0][0]))
            result = Pooler.query("""
            SELECT wal_fpi FROM pg_stat_wal;
            """)
            zbx.send(self.key_wal_fpi.format("[]"), int(result[0][0]))
            result = Pooler.query("""
            SELECT wal_buffers_full FROM pg_stat_wal;
            """)
            zbx.send(self.key_wal_buffers_full.format("[]"), int(result[0][0]))
            result = Pooler.query("""
            SELECT wal_write_time FROM pg_stat_wal;
            """)
            zbx.send(self.key_wal_write_time.format("[]"), int(result[0][0]))
            result = Pooler.query("""
            SELECT wal_sync_time FROM pg_stat_wal;
            """)
            zbx.send(self.key_wal_sync_time.format("[]"), int(result[0][0]))

    def items(self, template, dashboard=False):
        result = ""
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA_SPEED
        result += template.item({
            "name": "PostgreSQL WAL: Write Speed",
            "key": self.right_type(self.key_wall),
            "units": Plugin.UNITS.bytes_per_second,
            "delay": self.plugin_config("interval"),
            "delta": delta
        }) + template.item({
            "name": "PostgreSQL WAL: Count of WAL Files",
            "key": self.right_type(self.key_count_wall),
            "delay": self.plugin_config("interval")
        }) + template.item({
            "name": "PostgreSQL WAL: Records Generated",
            "key": self.right_type(self.key_wal_records),
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL WAL: Full Page Images Generated",
            "key": self.right_type(self.key_wal_fpi),
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL WAL: Buffers Full",
            "key": self.key_wal_buffers_full,
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL WAL: Write Time (ms)",
            "key": self.key_wal_write_time,
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL WAL: Sync Time (ms)",
            "key": self.key_wal_sync_time,
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL WAL: Sync Duty (%)",
            "key": self.key_wal_sync_duty,
            "value_type": Plugin.VALUE_TYPE.numeric_float,
            "units": Plugin.UNITS.percent,
            "type": Plugin.TYPE.CALCULATED,
            "params": "last(" + self.key_wal_sync_time + ")/10/" + self.plugin_config("interval")
        })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.right_type(self.key_wall),
                              "page": ZbxTemplate.dashboard_page_wal["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 2}
            }]

    def keys_and_queries(self, template_zabbix):
        result = []
        if LooseVersion(self.VersionPG) < LooseVersion("10"):
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wall.format("[*]"), self.query_xlog_lsn_diff))
            result.append(
                "{0},$2 $1 -c \"{1}\"".format(self.key_count_wall.format("[*]"),
                                              Pooler.SQL["count_wal_files"][0].format("xlog")))
        else:
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wall.format("[*]"), self.query_wal_lsn_diff))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_count_wall.format("[*]"),
                                                        Pooler.SQL["count_wal_files"][0].format("wal")))

        if LooseVersion(self.VersionPG) >= LooseVersion("14"):
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wal_records.format("[*]"), self.query_wal_records))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wal_fpi.format("[*]"), self.query_wal_fpi))
            result.append(
                "{0},$2 $1 -c \"{1}\"".format(self.key_wal_buffers_full.format("[*]"), self.query_wal_buffers_full))
            result.append(
                "{0},$2 $1 -c \"{1}\"".format(self.key_wal_write_time.format("[*]"), self.query_wal_write_time))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wal_sync_time.format("[*]"), self.query_wal_sync_time))
        return template_zabbix.key_and_query(result)
