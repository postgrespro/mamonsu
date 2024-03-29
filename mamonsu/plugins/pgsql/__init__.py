import mamonsu.lib.platform as platform

__all__ = ['bgwriter', 'connections', 'databases']
__all__ += ['health', 'instance', 'wal', 'replication']
__all__ += ['statements', 'pg_buffercache', 'wait_sampling']
__all__ += ['checkpoint', 'oldest', 'pg_locks']
__all__ += ['cfs']
__all__ += ['archive_command']
__all__ += ['autovacuum']
__all__ += ['prepared_transaction']
__all__ += ['relations_size']

if platform.LINUX:
    __all__ += ['memory_leak_diagnostic']

from . import *
