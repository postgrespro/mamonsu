# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate

NUMBER_NON_ACTIVE_SLOTS = 0


class Replication(Plugin):
    AgentPluginType = "pg"
    # key: (macro, value)
    plugin_macros = {
        "critical_lag_seconds": [("macro", "{$CRITICAL_LAG_SECONDS}"), ("value", 60 * 5)]
    }

    # get time of replication lag
    query_agent_replication_lag = """
    SELECT CASE WHEN NOT pg_is_in_recovery() OR coalesce(pg_last_{1}(), '0/00000000') = coalesce(pg_last_{2}(), '0/00000000')
                THEN 0
                ELSE extract (epoch FROM now() - coalesce(pg_last_xact_replay_timestamp(), now() - INTERVAL '{0} seconds'))
            END;
    """

    # for discovery rule for name of each replica
    key_lsn_replication_discovery = "pgsql.replication.discovery{0}"
    key_total_lag = "pgsql.replication.total_lag{0}"
    #  for PG 10 and higher
    key_flush = "pgsql.replication.flush_lag{0}"
    key_replay = "pgsql.replication.replay_lag{0}"
    key_write = "pgsql.replication.write_lag{0}"
    key_send = "pgsql.replication.send_lag{0}"
    key_receive = "pgsql.replication.receive_lag{0}"

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
            if Pooler.server_version_greater("10.0") and (Pooler.is_superuser() or Pooler.is_bootstraped()):
                result_lags = Pooler.run_sql_type("wal_lag_lsn",
                                                  args=[" (pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn))::int AS send_lag, "
                                                        "(pg_wal_lsn_diff(sent_lsn, flush_lsn))::int AS receive_lag, "
                                                        "(pg_wal_lsn_diff(sent_lsn, write_lsn))::int AS write_lag, "
                                                        "(pg_wal_lsn_diff(write_lsn, flush_lsn))::int AS flush_lag, "
                                                        "(pg_wal_lsn_diff(flush_lsn, replay_lsn))::int AS replay_lag, " if not Pooler.is_bootstraped() else
                                                        " send_lag, receive_lag, write_lag, flush_lag, replay_lag, ",
                                                        "wal", "lsn"])
                if result_lags:
                    lags = []
                    for info in result_lags:
                        lags.append({"{#APPLICATION_NAME}": info[0]})
                        zbx.send("pgsql.replication.total_lag[{0}]".format(info[0]), float(info[6]))
                        zbx.send("pgsql.replication.send_lag[{0}]".format(info[0]), float(info[1]))
                        zbx.send("pgsql.replication.receive_lag[{0}]".format(info[0]), float(info[2]))
                        zbx.send("pgsql.replication.write_lag[{0}]".format(info[0]), float(info[3]))
                        zbx.send("pgsql.replication.flush_lag[{0}]".format(info[0]), float(info[4]))
                        zbx.send("pgsql.replication.replay_lag[{0}]".format(info[0]), float(info[5]))
                    zbx.send("pgsql.replication.discovery[]", zbx.json({"data": lags}))
                    del lags
            elif Pooler.is_superuser() or Pooler.is_bootstraped():
                result_lags = Pooler.run_sql_type("wal_lag_lsn", args=[" ", "xlog", "location"])
                if result_lags:
                    lags = []
                    for info in result_lags:
                        lags.append({"{#APPLICATION_NAME}": info[0]})
                        zbx.send("pgsql.replication.total_lag[{0}]".format(info[0]), float(info[1]))
                    zbx.send("pgsql.replication.discovery[]", zbx.json({"data": lags}))
                    del lags
            else:
                self.disable_and_exit_if_not_superuser()

        non_active_slots = Pooler.query("""
        SELECT count(*)
        FROM pg_replication_slots
        WHERE active = 'false';
        """)
        zbx.send(self.key_non_active_slots.format("[]"), int(non_active_slots[0][0]))

    def items(self, template, dashboard=False):
        result = ""
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA_SPEED
        result += template.item({
            "name": "PostgreSQL Replication: Streaming Replication Lag",
            "key": self.right_type(self.key_replication, "sec"),
            "delay": self.plugin_config("interval")
        }) + template.item({
            "name": "PostgreSQL Replication: Count Non-Active Replication Slots",
            "key": self.right_type(self.key_non_active_slots),
            "value_type": self.VALUE_TYPE.numeric_unsigned,
        })
        if not dashboard:
            return result
        else:
            return []

    def macros(self, template, dashboard=False):
        result = ""
        for macro in self.plugin_macros.keys():
            result += template.mamonsu_macro(defaults=self.plugin_macros[macro])
        if not dashboard:
            return result
        else:
            return []

    def triggers(self, template, dashboard=False):
        triggers = template.trigger({
            "name": "PostgreSQL Replication: streaming lag too high on {HOSTNAME} (value={ITEM.LASTVALUE})",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_replication,
                                                          "sec") + ".last()}&gt;" +
                          self.plugin_macros["critical_lag_seconds"][0][1]
        }) + template.trigger({
            "name": "PostgreSQL Replication: number of non-active replication slots on {HOSTNAME} (value={ITEM.LASTVALUE})",
            "expression": "{#TEMPLATE:" + self.right_type(self.key_non_active_slots) + ".last()}&gt;" + str(
                NUMBER_NON_ACTIVE_SLOTS)
        })
        return triggers

    def discovery_rules(self, template, dashboard=False):
        rule = {
            "name": "PostgreSQL Replication Lag Discovery",
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
            {"key": self.right_type(self.key_send, var_discovery="{#APPLICATION_NAME},"),
             "name": "PostgreSQL Replication: {#APPLICATION_NAME} Send Lag - Time elapsed sending recent WAL locally",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_receive, var_discovery="{#APPLICATION_NAME},"),
             "name": "PostgreSQL Replication: {#APPLICATION_NAME} Receive Lag - Time elapsed between receiving recent WAL locally and receiving notification that "
                     "this standby server has flushed it",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_write, var_discovery="{#APPLICATION_NAME},"),
             "name": "PostgreSQL Replication: {#APPLICATION_NAME} Write Lag - Time elapsed between flushing recent WAL locally and receiving notification that "
                     "this standby server has written it",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_flush, var_discovery="{#APPLICATION_NAME},"),
             "name": "PostgreSQL Replication: {#APPLICATION_NAME} Flush Lag - Time elapsed between flushing recent WAL locally and receiving notification that "
                     "this standby server has written and flushed it",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_replay, var_discovery="{#APPLICATION_NAME},"),
             "name": "PostgreSQL Replication: {#APPLICATION_NAME} Replay Lag - Time elapsed between flushing recent WAL locally and receiving notification that "
                     "this standby server has written, flushed and applied",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2},
            {"key": self.right_type(self.key_total_lag, var_discovery="{#APPLICATION_NAME},"),
             "name": "PostgreSQL Replication: {#APPLICATION_NAME} Delta of Total Lag",
             "value_type": Plugin.VALUE_TYPE.numeric_float,
             "delay": self.plugin_config("interval"),
             "drawtype": 2}
        ]
        graphs = [
            {
                "name": "PostgreSQL Replication: Delta of Total Lag for {#APPLICATION_NAME}",
                "items": [
                    {"color": "A39B98",
                     "key": self.right_type(self.key_total_lag, var_discovery="{#APPLICATION_NAME},")},
                ]
            }
        ]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = []
        if LooseVersion(self.VersionPG) < LooseVersion("10"):
            result.append("{0},$2 $1 -c \"{1}\"".format("pgsql.replication_lag.sec[*]",
                                                        self.query_agent_replication_lag.format(
                                                            self.plugin_config("interval"), "xlog_receive_location",
                                                            "xlog_replay_location")))
        else:
            result.append("{0},$2 $1 -c \"{1}\"".format("pgsql.replication_lag.sec[*]",
                                                        self.query_agent_replication_lag.format(
                                                            self.plugin_config("interval"), "wal_receive_lsn",
                                                            "wal_replay_lsn")))
        return template_zabbix.key_and_query(result)
