# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler


class PgStatStatement(Plugin):
    AgentPluginType = "pg"
    # TODO: добавить выбор схемы
    query = """
    SELECT {0}
    FROM public.{1};
    """
    query_info = """
    SELECT {0}
    FROM public.pg_stat_statements_info;
    """
    key = "pgsql."
    # zbx_key, sql, desc, unit, delta, (Graph, color, side)
    Items = [
        ("stat[read_bytes]",
         "sum(shared_blks_read+local_blks_read+temp_blks_read)*8*1024",
         "read bytes/s", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: bytes", "BBBB00", 0)),
        ("stat[write_bytes]",
         "sum(shared_blks_written+local_blks_written"
         "+temp_blks_written)*8*1024",
         "write bytes/s", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: bytes", "00CC00", 0)),
        ("stat[dirty_bytes]",
         "sum(shared_blks_dirtied+local_blks_dirtied)*8*1024",
         "dirty bytes/s", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: bytes", "0000CC", 0)),

        ("stat[read_time]",
         "sum(blk_read_time)/float4(100)",
         "read io time", Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: spend time", "00CC00", 0)),
        ("stat[write_time]",
         "sum(blk_write_time)/float4(100)",
         "write io time", Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: spend time", "0000CC", 0)),
        ["stat[other_time]",
         "sum({0}-blk_read_time-blk_write_time)/float4(100)",
         "other (mostly cpu) time", Plugin.UNITS.s, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: spend time", "BBBB00", 0)]]

    Items_pg_13 = [
        ("stat[wal_bytes]",
         "sum(wal_bytes)",
         "amount of wal files", Plugin.UNITS.bytes_per_second, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: wal statistics", "BCC000", 0)),
        ("stat[wal_records]",
         "sum(wal_records)",
         "amount of wal records", Plugin.UNITS.none, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: wal statistics", "CC6600", 0)),
        ("stat[wal_fpi]",
         "sum(wal_fpi)",
         "full page writes", Plugin.UNITS.none, Plugin.DELTA.speed_per_second,
         ("PostgreSQL statements: wal statistics", "00CCCC", 0))
    ]

    Items_pg_14 = [
        ("stat_info[dealloc]",
         "dealloc",
         "the number of times the pg_stat_statements.max was exceeded",
         Plugin.UNITS.none,
         Plugin.DELTA.simple_change,
         ("PostgreSQL statements info: the number of times the pg_stat_statements.max was exceeded", "0000CC", 0)),
        ("stat_info[stats_reset]",
         "ceil(extract(epoch from stats_reset))",
         "last statistics reset",
         Plugin.UNITS.unixtime,
         Plugin.DELTA.as_is,
         ("PostgreSQL statements info: last statistics reset", "0000CC", 0))
    ]

    all_graphs = [
        ("PostgreSQL statements: bytes", None),
        ("PostgreSQL statements: spend time", 1),
        ("PostgreSQL statements: wal statistics", None)]

    def run(self, zbx):
        if not self.extension_installed("pg_stat_statements") or not self.extension_installed("pgpro_stats"):
            self.disable_and_exit_if_extension_is_not_installed(ext="pg_stat_statements/pgpro_stats")
        if Pooler.is_pgpro() or Pooler.is_pgpro_ee():
            extension = "pgpro_stats_statements"
        else:
            extension = "pg_stat_statements"
        if Pooler.server_version_greater("14"):
            self.Items[5][1] = self.Items[5][1].format("total_exec_time+total_plan_time")
            all_items = self.Items + self.Items_pg_13
            columns = [x[1] for x in all_items]
            info_items = self.Items_pg_14
            info_params = [x[1] for x in info_items]
            info_result = Pooler.query(self.query_info.format(", ".join(info_params)))
            for key, value in enumerate(info_result[0]):
                zbx_key, value = "pgsql.{0}".format(
                    info_items[key][0]), int(value)
                zbx.send(zbx_key, value, info_items[key][4])
        elif Pooler.server_version_greater("13"):
            self.Items[5][1] = self.Items[5][1].format("total_exec_time+total_plan_time")
            all_items = self.Items + self.Items_pg_13
            columns = [x[1] for x in all_items]
        else:
            self.Items[5][1] = self.Items[5][1].format("total_time")
            all_items = self.Items
            columns = [x[1] for x in all_items]
        result = Pooler.query(self.query.format(", ".join(columns), extension))
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
                "name": "PostgreSQL statements: {0}".format(item[2]),
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
                        "yaxisside": item[5][2]})
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
            if Pooler.is_pgpro() or Pooler.is_pgpro_ee():
                extension = "pgpro_stats_statements"
            else:
                extension = "pg_stat_statements"
            result = []
            if LooseVersion(self.VersionPG) < LooseVersion("13"):
                self.Items[5][1] = self.Items[5][1].format("total_time")
                all_items = self.Items
            else:
                self.Items[5][1] = self.Items[5][1].format("total_exec_time+total_plan_time")
                all_items = self.Items + self.Items_pg_13

            for i, item in enumerate(all_items):
                keys = item[0].split("[")
                result.append("{0}[*],$2 $1 -c \"{1}\"".format("{0}{1}.{2}".format(self.key, keys[0], keys[1][:-1]),
                                                               self.query.format(item[1], extension)))

            if LooseVersion(self.VersionPG) >= LooseVersion("14"):
                all_items = self.Items_pg_14
                for i, item in enumerate(all_items):
                    keys = item[0].split("[")
                    result.append("{0}[*],$2 $1 -c \"{1}\"".format("{0}{1}.{2}".format(self.key, keys[0], keys[1][:-1]),
                                                                   self.query_info.format(item[1])))
            return template_zabbix.key_and_query(result)
        else:
            return
