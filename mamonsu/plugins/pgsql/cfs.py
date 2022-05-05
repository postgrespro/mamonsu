# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Cfs(Plugin):
    AgentPluginType = "pg"
    ratioInterval, ratioCounter = 10, 0
    timeRatioInterval = ratioInterval * 60

    DEFAULT_CONFIG = {
        "force_enable": str(False)
    }

    query_cfs_compressed_ratio = """
    SELECT
        n.nspname || '.' || c.relname AS table_name,
        cfs_compression_ratio(c.oid::regclass) AS ratio,
        (pg_catalog.pg_total_relation_size(c.oid::regclass) - pg_catalog.pg_indexes_size(c.oid::regclass)) AS compressed_size
    FROM
        pg_catalog.pg_class AS c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.reltablespace IN (SELECT oid FROM pg_catalog.pg_tablespace WHERE spcoptions::text ~ 'compression')
        AND c.relkind IN ('r','v','m','S','f','p','')
        AND cfs_compression_ratio(c.oid::regclass) <> 'NaN'
    
    UNION ALL
    
    SELECT
        n.nspname || '.' || c.relname AS table_name,
        cfs_compression_ratio(c.oid::regclass) AS ratio,
        pg_catalog.pg_total_relation_size(c.oid::regclass) AS compressed_size -- pg_toast included
    FROM
        pg_catalog.pg_class AS c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.reltablespace IN (SELECT oid FROM pg_catalog.pg_tablespace WHERE spcoptions::text ~ 'compression')
        AND c.relkind = 'i'
        AND cfs_compression_ratio(c.oid::regclass) <> 'NaN';
    """

    query_cfs_activity = """
    SELECT
        cfs_gc_activity_processed_bytes(), -- written
        cfs_gc_activity_processed_pages() * 8 * 1024, -- scanned
        cfs_gc_activity_processed_files(), -- written
        cfs_gc_activity_scanned_files(); -- scanned
    """

    prev = {}

    def run(self, zbx):
        if self.plugin_config("force_enable"):
            if not self.get_boolean(self.plugin_config("force_enable")):
                self.disable_and_exit_if_not_pgpro_ee()

        # tick every 100 seconds
        if self.ratioCounter == self.ratioInterval:
            relations, compressed_size, non_compressed_size = [], 0, 0
            for db in Pooler.databases():
                for row in Pooler.query(self.query_cfs_compressed_ratio, db):
                    relation_name = "{0}.{1}".format(db, row[0])
                    relations.append({"{#COMPRESSED_RELATION}": relation_name})
                    compressed_size += row[2]
                    non_compressed_size += row[2] * row[1]
                    zbx.send("pgsql.cfs.compress_ratio[{0}]".format(relation_name), row[1])
            zbx.send("pgsql.cfs.discovery_compressed_relations[]", zbx.json({"data": relations}))
            if compressed_size > 0:
                zbx.send("pgsql.cfs.activity[total_compress_ratio]", non_compressed_size / compressed_size)
            else:
                zbx.send("pgsql.cfs.activity[total_compress_ratio]", 0.0)

            del (relations, compressed_size, non_compressed_size)
            self.ratioCounter = 0
        self.ratioCounter += 1

        info = Pooler.query(self.query_cfs_activity)[0]
        zbx.send("pgsql.cfs.activity[written_bytes]", info[0], delta=self.DELTA_SPEED, only_positive_speed=True)
        zbx.send("pgsql.cfs.activity[scanned_bytes]", info[1], delta=self.DELTA_SPEED, only_positive_speed=True)

        # calculate current compress ratio
        if ("written_bytes" in self.prev) and ("scanned_bytes" in self.prev):
            if info[0] > self.prev["written_bytes"] and info[1] > self.prev["scanned_bytes"]:
                val = (self.prev["scanned_bytes"] - info[1]) / ((self.prev["written_bytes"] - info[0]) * self.Interval)
                zbx.send("pgsql.cfs.activity[current_compress_ratio]", val)
        self.prev["written_bytes"] = info[0]
        self.prev["scanned_bytes"] = info[1]

        # information about files
        zbx.send("pgsql.cfs.activity[compressed_files]", info[2] * self.Interval, delta=self.DELTA_SPEED,
                 only_positive_speed=True)
        zbx.send("pgsql.cfs.activity[scanned_files]", info[3] * self.Interval, delta=self.DELTA_SPEED,
                 only_positive_speed=True)

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                "name": "PostgreSQL CFS: Written byte/s",
                "key": "pgsql.cfs.activity[written_bytes]",
                "units": self.UNITS.bytes_per_second,
                "delay": self.Interval
            }) + template.item({
                "name": "PostgreSQL CFS: Scanned byte/s",
                "key": "pgsql.cfs.activity[scanned_bytes]",
                "units": self.UNITS.bytes_per_second,
                "delay": self.Interval
            }) + template.item({
                "name": "PostgreSQL CFS: Compressed Files",
                "key": "pgsql.cfs.activity[compressed_files]",
                "units": self.UNITS.none,
                "delay": self.Interval
            }) + template.item({
                "name": "PostgreSQL CFS: Scanned Files",
                "key": "pgsql.cfs.activity[scanned_files]",
                "units": self.UNITS.none,
                "delay": self.Interval
            }) + template.item({
                "name": "PostgreSQL CFS: Current Ratio",
                "key": "pgsql.cfs.activity[current_compress_ratio]",
                "units": self.UNITS.none,
                "delay": self.Interval
            }) + template.item({
                "name": "PostgreSQL CFS: Total Ratio",
                "key": "pgsql.cfs.activity[total_compress_ratio]",
                "units": self.UNITS.none,
                "delay": self.Interval
            })
        else:
            return []

    def discovery_rules(self, template, dashboard=False):
        rule = {
            "name": "PostgreSQL CFS Discovery",
            "key": "pgsql.cfs.discovery_compressed_relations[]"
        }
        if Plugin.old_zabbix:
            rule["filter"] = "{#COMPRESSED_RELATION}:.*"
            conditions = []
        else:
            conditions = [{
                "condition": [{
                    "macro": "{#COMPRESSED_RELATION}",
                    "value": ".*",
                    "operator": 8,
                    "formulaid": "A"
                }]
            }]
        items = [{
            "key": "pgsql.cfs.compress_ratio[{#COMPRESSED_RELATION}]",
            "name": "PostgreSQL CFS: Relation {#COMPRESSED_RELATION} Compress Ratio",
            "delay": self.timeRatioInterval,
            "drawtype": 2
        }]
        graphs = [{
            "name": "PostgreSQL CFS: Relation {#COMPRESSED_RELATION} Compress Ratio",
            "delay": self.timeRatioInterval,
            "items": [{
                "color": "A39B98",
                "key": "pgsql.cfs.compress_ratio[{#COMPRESSED_RELATION}]"
            }]
        }]
        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs)
