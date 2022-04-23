# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate

NUMBER_NON_ACTIVE_SLOTS = 0


class Xlog(Plugin):
    AgentPluginType = "pg"
    DEFAULT_CONFIG = {
        "lag_more_than_in_sec": str(60 * 5)
    }

    # get amount of WAL since '0/00000000'
    query_wal_lsn_diff = """
    SELECT pg_catalog.pg_wal_lsn_diff(pg_catalog.pg_current_wal_lsn(), '0/00000000');
    """
    query_xlog_lsn_diff = """
    SELECT pg_catalog.pg_xlog_location_diff (pg_catalog.pg_current_xlog_location(), '0/00000000');
    """
    # get time of replication lag
    query_agent_replication_lag = """
    SELECT CASE WHEN NOT pg_is_in_recovery() OR coalesce(pg_last_{1}(), '0/00000000') = coalesce(pg_last_{2}(), '0/00000000')
                THEN 0
                ELSE extract (epoch FROM now() - coalesce(pg_last_xact_replay_timestamp(), now() - INTERVAL '{0} seconds'))
            END;
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

    # for discovery rule for name of each replica
    key_lsn_replication_discovery = "pgsql.replication.discovery{0}"
    key_total_lag = "pgsql.replication.total_lag{0}"
    #  for PG 10 and higher
    key_flush = "pgsql.replication.flush_lag{0}"
    key_replay = "pgsql.replication.replay_lag{0}"
    key_write = "pgsql.replication.write_lag{0}"

    # keys for PG 14 and higher
    key_wal_records = "pgsql.wal.records.count{0}"
    key_wal_fpi = "pgsql.wal.fpi.count{0}"
    key_wal_buffers_full = "pgsql.wal.buffers_full"
    key_wal_write_time = "pgsql.wal.write_time"
    key_wal_sync_time = "pgsql.wal.sync_time"
    key_wal_sync_duty = "pgsql.wal.sync_duty"

    key_wall = "pgsql.wal.write{0}"
    key_count_wall = "pgsql.wal.count{0}"
    key_replication = "pgsql.replication_lag{0}"
    key_non_active_slots = "pgsql.replication.non_active_slots{0}"

    def run(self, zbx):

        if Pooler.server_version_greater("10.0"):
            lag = Pooler.run_sql_type("replication_lag_slave_query",
                                      args=[self.plugin_config("interval"), "wal_receive_lsn", "wal_replay_lsn"])
        else:
            lag = Pooler.run_sql_type("replication_lag_slave_query",
                                      args=[self.plugin_config("interval"), "xlog_receive_location",
                                            "xlog_replay_location"])
        if lag[0][0] is not None:
            zbx.send("pgsql.replication_lag[sec]", float(lag[0][0]))

        if not Pooler.in_recovery():
            Pooler.run_sql_type("replication_lag_master_query")
            if Pooler.server_version_greater("10.0"):
                result = Pooler.query(self.query_wal_lsn_diff)
                result_lags = Pooler.run_sql_type("wal_lag_lsn",
                                                  args=[" flush_lag, replay_lag, write_lag, ", "wal", "lsn"])
                if result_lags:
                    lags = []
                    for info in result_lags:
                        lags.append({"{#APPLICATION_NAME}": info[0]})
                        zbx.send("pgsql.replication.flush_lag[{0}]".format(info[0]), info[1])
                        zbx.send("pgsql.replication.replay_lag[{0}]".format(info[0]), info[2])
                        zbx.send("pgsql.replication.write_lag[{0}]".format(info[0]), info[3])
                        zbx.send("pgsql.replication.total_lag[{0}]".format(info[0]), float(info[4]))
                    zbx.send("pgsql.replication.discovery[]", zbx.json({"data": lags}))
                    del lags
            else:
                result = Pooler.query(self.query_xlog_lsn_diff)
                result_lags = Pooler.run_sql_type("wal_lag_lsn", args=[" ", "xlog", "location"])
                if result_lags:
                    lags = []
                    for info in result_lags:
                        lags.append({"{#APPLICATION_NAME}": info[0]})
                        zbx.send("pgsql.replication.total_lag[{0}]".format(info[0]), float(info[1]))
                    zbx.send("pgsql.replication.discovery[]", zbx.json({"data": lags}))
                    del lags
            zbx.send(self.key_wall.format("[]"), float(result[0][0]), self.DELTA_SPEED)

        # count of xlog files
        if Pooler.server_version_greater("10.0"):
            result = Pooler.run_sql_type("count_wal_files", args=["wal"])
        else:
            result = Pooler.run_sql_type("count_wal_files", args=["xlog"])
        zbx.send(self.key_count_wall.format("[]"), int(result[0][0]))

        non_active_slots = Pooler.query("""
        SELECT count(*)
        FROM pg_replication_slots
        WHERE active = 'false';
        """)
        zbx.send(self.key_non_active_slots.format("[]"), int(non_active_slots[0][0]))

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
            "name": "PostgreSQL: wal write speed",
            "key": self.right_type(self.key_wall),
            "units": Plugin.UNITS.bytes_per_second,
            "delay": self.plugin_config("interval"),
            "delta": delta
        }) + template.item({
            "name": "PostgreSQL: streaming replication lag",
            "key": self.right_type(self.key_replication, "sec"),
            "delay": self.plugin_config("interval")
        }) + template.item({
            "name": "PostgreSQL: count of xlog files",
            "key": self.right_type(self.key_count_wall),
            "delay": self.plugin_config("interval")
        }) + template.item({
            "name": "PostgreSQL: count non-active replication slots",
            "key": self.right_type(self.key_non_active_slots),
            "value_type": self.VALUE_TYPE.numeric_unsigned,
        }) + template.item({
            "name": "PostgreSQL: wal records generated",
            "key": self.right_type(self.key_wal_records),
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL: wal full page images generated",
            "key": self.right_type(self.key_wal_fpi),
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL: wal buffers full",
            "key": self.key_wal_buffers_full,
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL: wal write time (ms)",
            "key": self.key_wal_write_time,
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL: wal sync time (ms)",
            "key": self.key_wal_sync_time,
            "value_type": self.VALUE_TYPE.numeric_unsigned,
            "delta": delta,
        }) + template.item({
            "name": "PostgreSQL: wal sync duty (%)",
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

    def triggers(self, template, dashboard=False):
        triggers = template.trigger({
            "name": "PostgreSQL streaming lag too high on {HOSTNAME} (value={ITEM.LASTVALUE})",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_replication,
                                                          "sec") + ".last()}&gt;" + self.plugin_config(
                "lag_more_than_in_sec")
        }) + template.trigger({
            "name": "PostgreSQL number of non-active replication slots on {HOSTNAME} (value={ITEM.LASTVALUE})",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_non_active_slots) + ".last()}&gt;" + str(
                NUMBER_NON_ACTIVE_SLOTS)
        })
        return triggers

    def discovery_rules(self, template, dashboard=False):
        rule = {
            "name": "Replication lag discovery",
            "key": self.key_lsn_replication_discovery.format("[{0}]".format(self.Macros[self.Type]))
        }
        if Plugin.old_zabbix:
            conditions = []
            rule["filter"] = "{#APPLICATION_NAME}:.*"
        else:
            conditions = [{
                "condition": [
                    {"macro": "{#APPLICATION_NAME}",
                     "value": ".*",
                     "operator": 8,
                     "formulaid": "A"}
                ]
            }]
        items = [
            {"key": self.right_type(self.key_flush, var_discovery="{#APPLICATION_NAME},"),
             "name": "Time elapsed between flushing recent WAL locally and receiving notification that "
                     "this standby server {#APPLICATION_NAME} has written and flushed it",
             "value_type": Plugin.VALUE_TYPE.text,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_replay, var_discovery="{#APPLICATION_NAME},"),
             "name": "Time elapsed between flushing recent WAL locally and receiving notification that "
                     "this standby server {#APPLICATION_NAME} has written, flushed and applied",
             "value_type": Plugin.VALUE_TYPE.text,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_write, var_discovery="{#APPLICATION_NAME},"),
             "name": "Time elapsed between flushing recent WAL locally and receiving notification that "
                     "this standby server {#APPLICATION_NAME} has written it",
             "value_type": Plugin.VALUE_TYPE.text,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_total_lag, var_discovery="{#APPLICATION_NAME},"),
             "name": "Delta of total lag for {#APPLICATION_NAME}",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2}
        ]
        graphs = [
            {
                "name": "Delta of total lag for {#APPLICATION_NAME}",
                "items": [
                    {"color": "8B817C",
                     "key": self.right_type(self.key_total_lag, var_discovery="{#APPLICATION_NAME},")},
                ]
            }
        ]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = []
        if LooseVersion(self.VersionPG) < LooseVersion("10"):
            result.append(
                "{0},$2 $1 -c \"{1}\"".format(self.key_count_wall.format("[*]"),
                                              Pooler.SQL["count_wal_files"][0].format("xlog")))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wall.format("[*]"), self.query_xlog_lsn_diff))
            result.append("{0},$2 $1 -c \"{1}\"".format("pgsql.replication_lag.sec[*]",
                                                        self.query_agent_replication_lag.format(
                                                            self.plugin_config("interval"), "xlog_receive_location",
                                                            "xlog_replay_location")))
        else:
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_count_wall.format("[*]"),
                                                        Pooler.SQL["count_wal_files"][0].format("wal")))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wall.format("[*]"), self.query_wal_lsn_diff))
            result.append("{0},$2 $1 -c \"{1}\"".format("pgsql.replication_lag.sec[*]",
                                                        self.query_agent_replication_lag.format(
                                                            self.plugin_config("interval"), "wal_receive_lsn",
                                                            "wal_replay_lsn")))
        if LooseVersion(self.VersionPG) >= LooseVersion("14"):
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wal_records.format("[*]"), self.query_wal_records))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wal_fpi.format("[*]"), self.query_wal_fpi))
            result.append(
                "{0},$2 $1 -c \"{1}\"".format(self.key_wal_buffers_full.format("[*]"), self.query_wal_buffers_full))
            result.append(
                "{0},$2 $1 -c \"{1}\"".format(self.key_wal_write_time.format("[*]"), self.query_wal_write_time))
            result.append("{0},$2 $1 -c \"{1}\"".format(self.key_wal_sync_time.format("[*]"), self.query_wal_sync_time))
        return template_zabbix.key_and_query(result)
