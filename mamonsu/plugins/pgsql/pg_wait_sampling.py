# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PgWaitSampling(Plugin):

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
order by count desc"""

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
order by count desc"""

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
order by count desc"""

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
