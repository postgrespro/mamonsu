# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgWaitSampling(Plugin):
    AgentPluginType = "pg"

    AllLockItems = [
        # (sql_key, zbx_key, name, color)
        ("lwlock", "all_lock[lwlock]",
         "Lightweight locks", "0000CC"),
        ("hwlock", "all_lock[hwlock]",
         "Heavyweight locks", "00CC00"),
        ("buffer", "all_lock[buffer]",
         "Buffer locks", "CC0000")
    ]

    AllLockQuery = {
        "pg_wait_sampling":
            """
            SELECT
                CASE
                    WHEN event_type = 'LWLockNamed' THEN 'lwlock'
                    WHEN event_type = 'LWLockTranche' THEN 'lwlock'
                    WHEN event_type = 'Lock' THEN 'hwlock'
                    ELSE 'buffer'
                END,
                sum(count) AS count
            FROM {extension_schema}.pg_wait_sampling_profile
            WHERE event_type is not null
            GROUP BY 1
            ORDER BY count DESC;
            """,
        "pgpro_stats":
            """
            WITH lock_table AS (
            SELECT setoflocks.key,
                   json_data.key AS lock_type,
                   json_data.value::int AS count
            FROM (SELECT key, value AS locktuple
                  FROM jsonb_each((SELECT wait_stats
                                   FROM {extension_schema}.pgpro_stats_totals
                                   WHERE object_type = 'cluster'))) setoflocks, 
            jsonb_each(setoflocks.locktuple) AS json_data)
            SELECT
                CASE
                    WHEN key = 'LWLockNamed' THEN 'lwlock'
                    WHEN key = 'LWLockTranche' THEN 'lwlock'
                    WHEN key = 'Lock' THEN 'hwlock'
                    ELSE 'buffer'
                END,
                sum(count) AS count
            FROM lock_table
            WHERE key <> 'Total'
            GROUP BY 1
            ORDER BY count DESC;
            """,
        "pgpro_stats_bootstrap":
            """
            SELECT lock_type, count FROM mamonsu.wait_sampling_all_locks();
            """
    }
    AllLockQuery["pg_wait_sampling_bootstrap"] = AllLockQuery["pg_wait_sampling"]

    HWLockItems = [
        # (sql_key, zbx_key, name, color)
        ("relation", "hwlock[relation]",
         "lock on a relation", "CC0000"),
        ("extend", "hwlock[extend]",
         "extend a relation", "00CC00"),
        ("page", "hwlock[page]",
         "lock on page", "0000CC"),
        ("tuple", "hwlock[tuple]",
         "lock on a tuple", "CC00CC"),
        ("transactionid", "hwlock[transactionid]",
         "transaction to finish", "000000"),
        ("virtualxid", "hwlock[virtualxid]",
         "virtual xid lock", "CCCC00"),
        ("speculative token", "hwlock[speculative_token]",
         "speculative insertion lock", "777777"),
        ("object", "hwlock[object]",
         "lock on database object", "770000"),
        ("userlock", "hwlock[userlock]",
         "userlock", "000077"),
        ("advisory", "hwlock[advisory]",
         "advisory user lock", "007700")
    ]

    HWLockQuery = {
        "pg_wait_sampling":
            """
                SELECT
                    event,
                    sum(count) AS count
                FROM {extension_schema}.pg_wait_sampling_profile
                WHERE event_type = 'Lock'
                GROUP BY 1
                ORDER BY count DESC;
                """,
        "pgpro_stats":
            """
            WITH lock_table AS (
            SELECT setoflocks.key,
                   json_data.key AS lock_type,
                   json_data.value::int AS count
            FROM (SELECT key, value AS locktuple
                  FROM jsonb_each((SELECT wait_stats
                                   FROM {extension_schema}.pgpro_stats_totals
                                   WHERE object_type = 'cluster'))) setoflocks, 
            jsonb_each(setoflocks.locktuple) AS json_data)
            SELECT
                lock_type,
                sum(count) AS count
            FROM lock_table
            WHERE key = 'Lock'
            GROUP BY 1
            ORDER BY count DESC;
            """,
        "pgpro_stats_bootstrap":
            """
            SELECT lock_type, count FROM mamonsu.wait_sampling_hw_locks();
            """
    }
    HWLockQuery["pg_wait_sampling_bootstrap"] = HWLockQuery["pg_wait_sampling"]

    LWLockItems = [
        # (sql_key, zbx_key, name, color)
        ("xid", "lwlock[xid]", "XID access", "BBBB00"),
        ("wal", "lwlock[wal]", "WAL access", "CC0000"),
        ("clog", "lwlock[clog]", "CLOG access", "00CC00"),
        ("replication", "lwlock[replication]", "Replication Locks", "FFFFCC"),
        ("buffer", "lwlock[buffer]", "Buffer operations", "0000CC"),
        ("other", "lwlock[other]", "Other operations", "007700")]

    LWLockQuery = {
        "pg_wait_sampling":
            """
            SELECT
                CASE
                    WHEN event = 'ProcArrayLock' THEN 'xid'
                    WHEN event = 'WALBufMappingLock' THEN 'wal'
                    WHEN event = 'WALWriteLock' THEN 'wal'
                    WHEN event = 'ControlFileLock' THEN 'wal'
                    WHEN event = 'wal_insert' THEN 'wal'
                    WHEN event = 'CLogControlLock' THEN 'clog'
                    WHEN event = 'clog' THEN 'clog'
                    WHEN event = 'SyncRepLock' THEN 'replication'
                    WHEN event = 'ReplicationSlotAllocationLock' THEN 'replication'
                    WHEN event = 'ReplicationSlotControlLock' THEN 'replication'
                    WHEN event = 'ReplicationOriginLock' THEN 'replication'
                    WHEN event = 'replication_origin' THEN 'replication'
                    WHEN event = 'replication_slot_io' THEN 'replication'
                    WHEN event = 'buffer_content' THEN 'buffer'
                    WHEN event = 'buffer_io' THEN 'buffer'
                    WHEN event = 'buffer_mapping' THEN 'buffer'
                    ELSE 'other'
                END,
                sum(count) AS count
            FROM {extension_schema}.pg_wait_sampling_profile
            WHERE event_type = 'LWLockTranche' OR event_type = 'LWLockNamed'
            GROUP BY 1
            ORDER BY count DESC;
            """,
        "pgpro_stats":
            """
            WITH lock_table AS (
            SELECT setoflocks.key,
                   json_data.key AS lock_type,
                   json_data.value::int AS count
            FROM (SELECT key, value AS locktuple
                  FROM jsonb_each((SELECT wait_stats
                                   FROM {extension_schema}.pgpro_stats_totals
                                   WHERE object_type = 'cluster'))) setoflocks, 
            jsonb_each(setoflocks.locktuple) AS json_data
            WHERE setoflocks.key IN ('Lock', 'LWLock', 'LWLockTranche', 'LWLockNamed'))
            SELECT
                CASE
                    WHEN lock_type = 'ProcArrayLock' THEN 'xid'
                    WHEN lock_type = 'WALBufMappingLock' THEN 'wal'
                    WHEN lock_type = 'WALWriteLock' THEN 'wal'
                    WHEN lock_type = 'ControlFileLock' THEN 'wal'
                    WHEN lock_type = 'wal_insert' THEN 'wal'
                    WHEN lock_type = 'CLogControlLock' THEN 'clog'
                    WHEN lock_type = 'clog' THEN 'clog'
                    WHEN lock_type = 'SyncRepLock' THEN 'replication'
                    WHEN lock_type = 'ReplicationSlotAllocationLock' THEN 'replication'
                    WHEN lock_type = 'ReplicationSlotControlLock' THEN 'replication'
                    WHEN lock_type = 'ReplicationOriginLock' THEN 'replication'
                    WHEN lock_type = 'replication_origin' THEN 'replication'
                    WHEN lock_type = 'replication_slot_io' THEN 'replication'
                    WHEN lock_type = 'buffer_content' THEN 'buffer'
                    WHEN lock_type = 'buffer_io' THEN 'buffer'
                    WHEN lock_type = 'buffer_mapping' THEN 'buffer'
                    ELSE 'other'
                END,
                sum(count) AS count
            FROM lock_table
            GROUP BY 1
            ORDER BY count DESC;
            """,
        "pgpro_stats_bootstrap":
            """
            SELECT lock_type, count FROM mamonsu.wait_sampling_lw_locks();
            """
    }
    LWLockQuery["pg_wait_sampling_bootstrap"] = LWLockQuery["pg_wait_sampling"]

    def run(self, zbx):

        def find_and_send(where, what, zbx):
            for item in what:
                item_found = False
                for result in where:
                    if item[0] == result[0]:
                        zbx.send(
                            "pgsql.{0}".format(item[1]),
                            float(result[1]), Plugin.DELTA.speed_per_second)
                        item_found = True
                        break
                if not item_found:
                    zbx.send(
                        "pgsql.{0}".format(item[1]),
                        float(0), Plugin.DELTA.speed_per_second)

        if not self.extension_installed("pg_wait_sampling") or not self.extension_installed("pgpro_stats"):
            self.disable_and_exit_if_extension_is_not_installed(ext="pg_wait_sampling/pgpro_stats")
        if Pooler.is_pgpro() or Pooler.is_pgpro_ee():
            if not Pooler.is_bootstraped():
                self.disable_and_exit_if_not_superuser()
            extension = "pgpro_stats"
        else:
            extension = "pg_wait_sampling"

        extension_schema = self.extension_schema(extension=extension)

        find_and_send(Pooler.query(
            self.AllLockQuery[extension + "_bootstrap"] if Pooler.is_bootstraped() else self.AllLockQuery[
                extension].format(extension_schema=extension_schema)), self.AllLockItems, zbx)
        find_and_send(Pooler.query(
            self.HWLockQuery[extension + "_bootstrap"] if Pooler.is_bootstraped() else self.HWLockQuery[
                extension].format(extension_schema=extension_schema)), self.HWLockItems, zbx)
        find_and_send(Pooler.query(
            self.LWLockQuery[extension + "_bootstrap"] if Pooler.is_bootstraped() else self.LWLockQuery[
                extension].format(extension_schema=extension_schema)), self.LWLockItems, zbx)

    def items(self, template, dashboard=False):
        result = ""
        for item in (self.AllLockItems + self.LWLockItems + self.HWLockItems):
            result += template.item({
                "key": "pgsql.{0}".format(item[1]),
                "name": "PostgreSQL waits: {0}".format(item[2]),
                "delay": self.plugin_config("interval"),
                "value_type": self.VALUE_TYPE.numeric_float})
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        result = ""
        for graph_name, graph_items in [
            ("PostgreSQL waits: Locks by type", self.AllLockItems),
            ("PostgreSQL waits: Heavyweight locks", self.HWLockItems),
            ("PostgreSQL waits: Lightweight locks", self.LWLockItems)]:
            items = []
            for item in graph_items:
                items.append({
                    "key": "pgsql.{0}".format(item[1]),
                    "color": item[3]})
            result += template.graph({
                "name": graph_name,
                "type": 1,
                "items": items})
        if not dashboard:
            return result
        else:
            return []
