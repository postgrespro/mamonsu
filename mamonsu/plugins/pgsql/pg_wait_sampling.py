# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgWaitSampling(Plugin):
    AgentPluginType = 'pg'
    # queries for zabbix agent
    query_agent_discovery_all_lock = "SELECT json_build_object ('data',json_agg(json_build_object('{#ALL_LOCK}', " \
                                     "t.event_type)))  from (SELECT DISTINCT (CASE WHEN event_type = 'LWLockNamed' " \
                                     "THEN 'lwlock' WHEN event_type = 'LWLockTranche' THEN 'lwlock'  " \
                                     "WHEN event_type = 'Lock' THEN 'hwlock' ELSE 'buffer' END) AS event_type " \
                                     "FROM pg_wait_sampling_profile where event_type is not null) AS t;"

    query_agent_discovery_hw_lock = "SELECT json_build_object ('data',json_agg(json_build_object('{#HW_LOCK}'," \
                                    " event))) from pg_wait_sampling_profile where event_type = 'Lock';"

    query_agent_discovery_lw_lock = "SELECT json_build_object ('data',json_agg(json_build_object('{#LW_LOCK}',t.event)))" \
                                    "  from (SELECT DISTINCT ( CASE WHEN event = 'ProcArrayLock' THEN 'xid' " \
                                    "WHEN event = 'WALBufMappingLock' THEN 'wal' WHEN event = 'WALWriteLock' " \
                                    "THEN 'wal' WHEN event = 'ControlFileLock' THEN 'wal' WHEN event = 'wal_insert' " \
                                    "THEN 'wal'  WHEN event = 'CLogControlLock' THEN 'clog' WHEN event = 'SyncRepLock' " \
                                    "THEN 'replication'   WHEN event = 'ReplicationSlotAllocationLock' " \
                                    "THEN 'replication' WHEN event = 'ReplicationSlotControlLock' THEN 'replication'  " \
                                    "WHEN event = 'ReplicationOriginLock' THEN 'replication'  " \
                                    "WHEN event = 'replication_origin' THEN 'replication'   " \
                                    "WHEN event = 'replication_slot_io' THEN 'replication' " \
                                    "WHEN event = 'buffer_content' THEN 'buffer'  " \
                                    "WHEN event = 'buffer_io' THEN 'buffer' " \
                                    "WHEN event = 'buffer_mapping' THEN 'buffer' ELSE 'other' END) " \
                                    "AS event from pg_wait_sampling_profile " \
                                    " where event_type = 'LWLockTranche' or event_type = 'LWLockNamed') as t;"
    query_agent_all_lock = "select sum(count) as count from pg_wait_sampling_profile  where " \
                           "CASE  " \
                           "WHEN 'lwlock' = :'p1' THEN event_type = 'LWLockNamed' or event_type = 'LWLockTranche'   " \
                           "WHEN 'hwlock' = :'p1' THEN  event_type = 'Lock' " \
                           "WHEN 'buffer' = :'p1' THEN event_type != 'LWLockNamed' and event_type != 'LWLockTranche' " \
                           "and event_type != 'Lock' " \
                           "END;"
    query_agent_hw_lock = "select sum(count) as count from pg_wait_sampling_profile  " \
                          "where  event = :'p1' AND event_type = 'Lock';"
    query_agent_lw_lock = "select sum(count) as count from pg_wait_sampling_profile  where " \
                          "CASE  " \
                          "WHEN 'xid' = :'p1' THEN event = 'ProcArrayLock' " \
                          "WHEN 'wal' = :'p1' THEN  event = 'WALBufMappingLock' OR event = 'WALWriteLock' " \
                          "OR event = 'ControlFileLock'  OR event = 'wal_insert' " \
                          "WHEN 'clog' = :'p1' THEN event = 'CLogControlLock' OR  event = 'clog' " \
                          "WHEN 'replication' = :'p1'  THEN event = 'CLogControlLock' OR event = 'CLogControlLock'" \
                          " OR event = 'CLogControlLock' OR event = 'CLogControlLock' OR event = 'CLogControlLock' " \
                          " WHEN 'buffer' = :'p1' THEN  event = 'buffer_content' OR event = 'buffer_io' " \
                          "OR event = 'buffer_mapping' " \
                          "WHEN 'other' = ':p1' THEN event IS NOT NULL " \
                          "END; "

    key_all_lock_discovery = "pgsql.all_lock.discovery{0}"
    key_all_lock = "pgsql.all_lock{0}"
    key_hw_lock_discovery = "pgsql.hw_lock.discovery{0}"
    key_hw_lock = "pgsql.hw_lock{0}"
    key_lw_lock_discovery = "pgsql.lw_lock.discovery{0}"
    key_lw_lock = "pgsql.lw_lock{0}"

    AllLockItems = [
        # (sql_key, zbx_key, name, color)
        ('lwlock', 'all_lock[lwlock]',
         'Lightweight locks', '0000CC'),
        ('hwlock', 'all_lock[hwlock]',
         'Heavyweight locks', '00CC00'),
        ('buffer', 'all_lock[buffer]',
         'Buffer locks', 'CC0000')
    ]

    AllLockQuery = """
select
    CASE
        WHEN event_type = 'LWLockNamed' THEN 'lwlock'
        WHEN event_type = 'LWLockTranche' THEN 'lwlock'
        WHEN event_type = 'Lock' THEN 'hwlock'
        ELSE 'buffer'
    END,
    sum(count) as count
from pg_wait_sampling_profile
    where event_type is not null
group by 1
order by count desc;"""

    HWLockItems = [
        # (sql_key, zbx_key, name, color)
        ('relation', 'hwlock[relation]',
         'lock on a relation', 'CC0000'),
        ('extend', 'hwlock[extend]',
         'extend a relation', '00CC00'),
        ('page', 'hwlock[page]',
         'lock on page', '0000CC'),
        ('tuple', 'hwlock[tuple]',
         'lock on a tuple', 'CC00CC'),
        ('transactionid', 'hwlock[transactionid]',
         'transaction to finish', '000000'),
        ('virtualxid', 'hwlock[virtualxid]',
         'virtual xid lock', 'CCCC00'),
        ('speculative token', 'hwlock[speculative_token]',
         'speculative insertion lock', '777777'),
        ('object', 'hwlock[object]',
         'lock on database object',
         '770000'),
        ('userlock', 'hwlock[userlock]',
         'userlock', '000077'),
        ('advisory', 'hwlock[advisory]',
         'advisory user lock', '007700')
    ]

    HWLockQuery = """
select
    event,
    sum(count) as count
from pg_wait_sampling_profile
    where event_type = 'Lock'
group by 1
order by count desc;"""

    LWLockItems = [
        # (sql_key, zbx_key, name, color)
        ('xid', 'lwlock[xid]', 'XID access', 'BBBB00'),
        ('wal', 'lwlock[wal]', 'WAL access', 'CC0000'),
        ('clog', 'lwlock[clog]', 'CLOG access', '00CC00'),
        ('replication', 'lwlock[replication]', 'Replication Locks', 'FFFFCC'),
        ('buffer', 'lwlock[buffer]', 'Buffer operations', '0000CC'),
        ('other', 'lwlock[other]', 'Other operations', '007700')]

    LWLockQuery = """
select
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
    sum(count) as count
from pg_wait_sampling_profile
    where event_type = 'LWLockTranche' or event_type = 'LWLockNamed'
group by 1
order by count desc;"""

    def run(self, zbx):

        def find_and_send(where, what, zbx):
            for item in what:
                item_found = False
                for result in where:
                    if item[0] == result[0]:
                        zbx.send(
                            'pgsql.{0}'.format(item[1]),
                            float(result[1]), Plugin.DELTA.speed_per_second)
                        item_found = True
                        break
                if not item_found:
                    zbx.send(
                        'pgsql.{0}'.format(item[1]),
                        float(0), Plugin.DELTA.speed_per_second)

        self.disable_and_exit_if_extension_is_not_installed('pg_wait_sampling')

        find_and_send(Pooler.query(self.AllLockQuery), self.AllLockItems, zbx)
        find_and_send(Pooler.query(self.HWLockQuery), self.HWLockItems, zbx)
        find_and_send(Pooler.query(self.LWLockQuery), self.LWLockItems, zbx)

    def items(self, template):
        result = ''
        for item in (self.AllLockItems + self.LWLockItems + self.HWLockItems):
            result += template.item({
                'key': 'pgsql.{0}'.format(item[1]),
                'name': 'PostgreSQL waits: {0}'.format(item[2]),
                'value_type': self.VALUE_TYPE.numeric_float})
        return result

    def graphs(self, template):
        result = ''
        for graph_name, graph_items in [
            ('PostgreSQL waits: Locks by type', self.AllLockItems),
            ('PostgreSQL waits: Heavyweight locks', self.HWLockItems),
            ('PostgreSQL waits: Lightweight locks', self.LWLockItems)]:
            items = []
            for item in graph_items:
                items.append({
                    'key': 'pgsql.{0}'.format(item[1]),
                    'color': item[3]})
            result += template.graph({
                'name': graph_name, 'type': 1, 'items': items})
        return result

    # discovery rule for agent type
    def discovery_rules(self, template):
        rule = ({
            'name': 'AllLockItems',
            'key': self.key_all_lock_discovery.format('[{0}]'.format(self.Macros[self.Type])),
            'filter': '{#ALL_LOCK}:.*'
        })

        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA.speed_per_second
        items = []
        for item in (self.AllLockItems):
            keys = item[1].split('[')
            items.append({
                'key': self.right_type(self.key_all_lock, keys[1][:-1], var_discovery="{#ALL_LOCK},"),
                'name': 'PostgreSQL waits: {0}'.format(item[2]),
                'value_type': self.VALUE_TYPE.numeric_float,
                'delta': delta})
        graphs = []
        for graph_name, graph_items in [
            ('PostgreSQL waits: Locks by type', self.AllLockItems)]:
            items = []
            # for item in graph_items:
            # keys = item[1].split('[')
            items.append({
                'name': 'PostgreSQL Locks : {#ALL_LOCK}',
                'key': self.right_type(self.key_all_lock, var_discovery="{#ALL_LOCK},"),
                'color': item[3]})
            graphs.append({'name': graph_name, 'type': 1, 'items': items})

        return template.discovery_rule(rule=rule, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append(
            '{0},$2 $1 -c "{1}"'.format(self.key_all_lock_discovery.format("[*]"), self.query_agent_discovery_all_lock))
        result.append(
            '{0},echo "{1}" | $3 $2 -v p1="$1"'.format(self.key_all_lock.format("[*]"), self.query_agent_all_lock))
        return template_zabbix.key_and_query(result)
