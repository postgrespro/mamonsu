# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class WaitSampling(Plugin):

    AllLockItems = [
        # (key, [wait_event_type], name, color)
        ('pgsql.all_lock[lwlock]', ['LWLockNamed', 'LWLockTranche'],
            'PostgreSQL: Lightweight locks', '0000CC'),
        ('pgsql.all_lock[hwlock]', ['Lock'],
            'PostgreSQL: Heavyweight locks', '00CC00'),
        ('pgsql.all_lock[buffer]', ['BufferPin'],
            'PostgreSQL: Buffer locks', 'CC0000')
    ]

    HWLockItems = [
        # (key, wait_event, name, color)
        ('pgsql.hwlock[relation]', 'relation',
            'Waiting to acquire a lock on a relation', 'CC0000'),
        ('pgsql.hwlock[extend]', 'extend',
            'Waiting to extend a relation', '00CC00'),
        ('pgsql.hwlock[page]', 'page',
            'Waiting to acquire a lock on page of a relation', '0000CC'),
        ('pgsql.hwlock[tuple]', 'tuple',
            'Waiting to acquire a lock on a tuple', 'CC00CC'),
        ('pgsql.hwlock[transactionid]', 'transactionid',
            'Waiting for a transaction to finish', '000000'),
        ('pgsql.hwlock[virtualxid]', 'virtualxid',
            'Waiting to acquire a virtual xid lock', 'CCCC00'),
        ('pgsql.hwlock[speculative_token]', 'speculative token',
            'Waiting to acquire a speculative insertion lock', '777777'),
        ('pgsql.hwlock[object]', 'object',
            'Waiting to acquire a lock on a non-relation database object',
            '770000'),
        ('pgsql.hwlock[userlock]', 'userlock',
            'Waiting to acquire a userlock', '000077'),
        ('pgsql.hwlock[advisory]', 'advisory',
            'Waiting to acquire an advisory user lock', '007700')
    ]

    LWLockItems = [
        ('pgsql.lwlock[wal]' 'WAL Locks', 'CC0000',
            ['WALBufMappingLock', 'WALWriteLock',
                'ControlFileLock', 'wal_insert']),
        ('pgsql.lwlock[clog]' 'CLOG Locks', '00CC00',
            ['CLogControlLock', 'clog']),
        ('pgsql.lwlock[replication]' 'Replication Locks', '0000CC',
            ['SyncRepLock', 'ReplicationSlotAllocationLock',
                'ReplicationSlotControlLock', 'ReplicationOriginLock',
                'replication_origin', 'replication_slot_io']),
        ('pgsql.lwlock[buffer]' 'Buffer operations', '0000CC',
            ['buffer_content', 'buffer_io', 'buffer_mapping']),
    ]

    def run(self, zbx):
        Pooler.query("""
select
    event_type,
    sum(count) as count
from pg_wait_sampling_profile
    where event_type is not null
group by event_type
order by count desc""")
