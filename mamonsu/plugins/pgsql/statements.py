# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler


class Statements(Plugin):
    AgentPluginType = "pg"
    query = {
        "pg_stat_statements":
            """
            SELECT {metrics}
            FROM {extension_schema}.pg_stat_statements;
            """,
        "pgpro_stats":
            """
            SELECT {metrics}
            FROM {extension_schema}.pgpro_stats_totals
            WHERE object_type = 'cluster';
            """,
        "pgpro_stats_bootstrap":
            """
            SELECT {columns} FROM mamonsu.statements_pro();
            """
    }
    query["pg_stat_statements_bootstrap"] = query["pg_stat_statements"]

    query_info = """
    SELECT {metrics}
    FROM {extension_schema}.pg_stat_statements_info;
    """
    key = "pgsql."
    # zbx_key, sql, desc, unit, delta, (Graph, color, side)
    Items = [
        ("stat[read_bytes]",
         "sum(shared_blks_read+local_blks_read+temp_blks_read)*8*1024",
         "Read bytes/s", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: Bytes", "7EB29B", 0)),
        ("stat[write_bytes]",
         "sum(shared_blks_written+local_blks_written"
         "+temp_blks_written)*8*1024",
         "Write bytes/s", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: Bytes", "793F5D", 0)),
        ("stat[dirty_bytes]",
         "sum(shared_blks_dirtied+local_blks_dirtied)*8*1024",
         "Dirty bytes/s", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: Bytes", "9C8A4E", 0)),

        ("stat[read_time]",
         "sum(blk_read_time)/float4(100)",
         "Read IO Time", Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: Spend Time", "7EB29B", 0)),
        ("stat[write_time]",
         "sum(blk_write_time)/float4(100)",
         "Write IO Time", Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: Spend Time", "793F5D", 0)),
        ["stat[other_time]",
         "sum({0}-blk_read_time-blk_write_time)/float4(100)",
         "Other (mostly CPU) Time", Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: Spend Time", "9C8A4E", 0)]]

    Items_pg_13 = [
        ("stat[wal_bytes]",
         "sum(wal_bytes)",
         "Amount of WAL Files", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: WAL Statistics", "00B0B8", 0)),
        ("stat[wal_records]",
         "sum(wal_records)",
         "Amount of WAL Records", Plugin.UNITS.none, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: WAL Statistics", "0082A5", 0)),
        ("stat[wal_fpi]",
         "sum(wal_fpi)",
         "Full Page Writes", Plugin.UNITS.none, Plugin.DELTA.speed_per_second,
         ("PostgreSQL Statements: WAL Statistics", "9C8A4E", 0))
    ]

    Items_pg_14 = [
        ("stat_info[dealloc]",
         "dealloc",
         "Nnumber of Times pg_stat_statements.max Was Exceeded",
         Plugin.UNITS.none,
         Plugin.DELTA.simple_change,
         ("PostgreSQL Statements Info: Number of Times pg_stat_statements.max Was Exceeded", "793F5D", 0)),
        ("stat_info[stats_reset]",
         "ceil(extract(epoch from stats_reset))",
         "Last Statistics Reset Time",
         Plugin.UNITS.unixtime,
         Plugin.DELTA.as_is,
         ("PostgreSQL Statements Info: Last Statistics Reset Time", "9C8A4E", 0))
    ]

    all_graphs = [
        ("PostgreSQL Statements: Bytes", None),
        ("PostgreSQL Statements: Spend Time", 1),
        ("PostgreSQL Statements: WAL Statistics", None)]

    def run(self, zbx):
        if not self.extension_installed("pg_stat_statements") or not self.extension_installed("pgpro_stats"):
            self.disable_and_exit_if_extension_is_not_installed(ext="pg_stat_statements/pgpro_stats")
        if (Pooler.is_pgpro() or Pooler.is_pgpro_ee()) and Pooler.server_version_greater("12"):
            if not Pooler.is_bootstraped():
                self.disable_and_exit_if_not_superuser()
            extension = "pgpro_stats"
        else:
            extension = "pg_stat_statements"

        extension_schema = self.extension_schema(extension=extension)

        # TODO: add 13 and 14 items when pgpro_stats added new WAL metrics
        all_items = self.Items
        if Pooler.server_version_greater("14"):
            self.Items[5][1] = self.Items[5][1].format("total_exec_time+total_plan_time")
            if not Pooler.is_pgpro() or not Pooler.is_pgpro_ee():
                all_items += self.Items_pg_13
                info_items = self.Items_pg_14
                info_params = [x[1] for x in info_items]
                info_result = Pooler.query(
                    self.query_info.format(metrics=(", ".join(info_params)), extension_schema=extension_schema))
                for key, value in enumerate(info_result[0]):
                    zbx_key, value = "pgsql.{0}".format(
                        info_items[key][0]), int(value)
                    zbx.send(zbx_key, value, info_items[key][4])
            columns = [x[1] for x in all_items]
        elif Pooler.server_version_greater("13"):
            self.Items[5][1] = self.Items[5][1].format("total_exec_time+total_plan_time")
            if not Pooler.is_pgpro() or not Pooler.is_pgpro_ee():
                all_items += self.Items_pg_13
            columns = [x[1] for x in all_items]
        else:
            self.Items[5][1] = self.Items[5][1].format("total_time")
            columns = [x[1] for x in all_items]
        result = Pooler.query(self.query[extension + "_bootstrap"].format(
            columns=", ".join([x[0][x[0].find("[") + 1:x[0].find("]")] for x in all_items]),
            metrics=(", ".join(columns)), extension_schema=extension_schema) if Pooler.is_bootstraped() else self.query[
            extension].format(metrics=(", ".join(columns)), extension_schema=extension_schema))
        for key, value in enumerate(result[0]):
            zbx_key, value = "pgsql.{0}".format(all_items[key][0]), int(value)
            zbx.send(zbx_key, value, all_items[key][4])

    def items(self, template, dashboard=False):
        result = ""
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA.speed_per_second
        for item in self.Items + self.Items_pg_13 + self.Items_pg_14:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[0].split("[")
            result += template.item({
                "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                "name": "PostgreSQL Statements: {0}".format(item[2]),
                "value_type": self.VALUE_TYPE.numeric_float,
                "units": item[3],
                "delay": self.plugin_config("interval"),
                "delta": delta})
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        result = ""
        for graph_item in self.all_graphs:
            items = []
            for item in self.Items + self.Items_pg_13:
                if item[5][0] == graph_item[0]:
                    keys = item[0].split("[")
                    items.append({
                        "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                        "color": item[5][1],
                        "yaxisside": item[5][2],
                    "drawtype": 2})
            # create graph
            graph = {
                "name": graph_item[0],
                "items": items}
            if graph_item[1] is not None:
                graph["type"] = graph_item[1]
            result += template.graph(graph)
        if not dashboard:
            return result
        else:
            return []

    def keys_and_queries(self, template_zabbix):
        if self.extension_installed("pg_stat_statements") or not self.extension_installed("pgpro_stats"):
            if (Pooler.is_pgpro() or Pooler.is_pgpro_ee()) and Pooler.server_version_greater("12"):
                if not Pooler.is_bootstraped():
                    self.disable_and_exit_if_not_superuser()
                extension = "pgpro_stats"
            else:
                extension = "pg_stat_statements"

            extension_schema = self.extension_schema(extension=extension)

            result = []
            all_items = self.Items
            if LooseVersion(self.VersionPG) < LooseVersion("13"):
                self.Items[5][1] = self.Items[5][1].format("total_time")
            else:
                self.Items[5][1] = self.Items[5][1].format("total_exec_time+total_plan_time")
                if Pooler.is_pgpro() or Pooler.is_pgpro_ee():
                    all_items += self.Items_pg_13

            for i, item in enumerate(all_items):
                keys = item[0].split("[")
                result.append("{0}[*],$2 $1 -c \"{1}\"".format("{0}{1}.{2}".format(self.key, keys[0], keys[1][:-1]),
                                                               self.query[extension + "_bootstrap"].format(
                                                                   columns=", ".join(
                                                                       [x[0][x[0].find("[") + 1:x[0].find("]")] for x in
                                                                        all_items]), metrics=(", ".join(columns)),
                                                                   extension_schema=extension_schema) if Pooler.is_bootstraped() else
                                                               self.query[extension].format(
                                                                   metrics=(", ".join(columns)),
                                                                   extension_schema=extension_schema)))

            if LooseVersion(self.VersionPG) >= LooseVersion("14"):
                if Pooler.is_pgpro() or Pooler.is_pgpro_ee():
                    all_items += self.Items_pg_14
                for i, item in enumerate(all_items):
                    keys = item[0].split("[")
                    result.append("{0}[*],$2 $1 -c \"{1}\"".format("{0}{1}.{2}".format(self.key, keys[0], keys[1][:-1]),
                                                                   self.query_info.format(metrics=(item[1]),
                                                                                          extension_schema=extension_schema)))
            return template_zabbix.key_and_query(result)
        else:
            return
