# Mamonsu: metrics

**Metrics:**
- [Mamonsu health metrics](#mamonsu-health-metrics)
  - [Items](#items)
  - [Triggers](#triggers)
- [System metrics](#system-metrics)
  - [*nix](#nix)
    - [Items](#items-1)
    - [Discovery Rules](#discovery-rules)
    - [Graphs](#graphs)
    - [Triggers](#triggers-1)
  - [Windows](#windows)
    - [Items](#items-2)
    - [Discovery Rules](#discovery-rules-1)
- [PostgreSQL metrics](#postgresql-metrics)
  - [Archiving](#archiving)
    - [Items](#items-3)
    - [Graphs](#graphs-1)
    - [Triggers](#triggers-2)
  - [Autovacuum](#autovacuum)
    - [Items](#items-4)
  - [Background Writer](#background-writer)
    - [Items](#items-5)
    - [Graphs](#graphs-2)
  - [Blocks](#blocks)
    - [Items](#items-6)
    - [Graphs](#graphs-3)
  - [Checkpoints](#checkpoints)
    - [Items](#items-7)
    - [Graphs](#graphs-4)
    - [Triggers](#triggers-3)
  - [Connections](#connections)
    - [Items](#items-8)
    - [Graphs](#graphs-5)
    - [Triggers](#triggers-4)
  - [Databases](#databases)
    - [Discovery Rules](#discovery-rules-2)
  - [Events](#events)
    - [Items](#items-9)
    - [Graphs](#graphs-6)
  - [Health](#health)
    - [Items](#items-10)
    - [Triggers](#triggers-5)
  - [Memory Leak](#memory-leak)
    - [Items](#items-11)
    - [Triggers](#triggers-6)
  - [pg_buffercache](#pg_buffercache)
    - [Items](#items-12)
    - [Graphs](#graphs-7)
  - [pg_locks](#pg_locks)
    - [Items](#items-13)
    - [Graphs](#graphs-8)
  - [pg_stat_statements](#pg_stat_statements)
    - [Items](#items-14)
    - [Graphs](#graphs-9)
  - [Prepared Transactions](#prepared-transactions)
    - [Items](#items-15)
    - [Graphs](#graphs-10)
    - [Triggers](#triggers-7)
  - [Relations](#relations)
    - [Discovery Rules](#discovery-rules-3)
  - [Replication](#replication)
    - [Items](#items-16)
    - [Discovery Rules](#discovery-rules-4)
    - [Triggers](#triggers-8)
  - [Temp Files](#temp-files)
    - [Items](#items-17)
    - [Graphs](#graphs-11)
  - [Transactions](#transactions)
    - [Items](#items-18)
    - [Triggers](#triggers-9)
  - [Tuples](#tuples)
    - [Items](#items-19)
    - [Graphs](#graphs-12)
  - [WAL](#wal)
    - [Items](#items-20)
- [Postgres Pro metrics](#postgres-pro-metrics)
  - [Compressed File System](#compressed-file-system)
    - [Items](#items-21)
    - [Discovery Rules](#discovery-rules-5)
  - [pg_wait_sampling](#pg_wait_sampling)
    - [Items](#items-22)
    - [Graphs](#graphs-13)
    
## Mamonsu Health metrics

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_memory_usage = 40 Mb

### Items

1. **Plugin Errors**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Mamonsu: plugin errors</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>mamonsu.plugin.errors[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Text</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

    *Plugin Errors* collects Mamonsu error messages. It might be PostgreSQL extensions errors, rights errors, etc.


2. **Plugin Health**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Mamonsu: plugin keep alive</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>mamonsu.plugin.keepalive[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>
   
    *Plugin Health* indicates that Mamonsu is running.


3. **RSS Memory Maximum Usage (for UNIX only)**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Mamonsu: rss memory max usage</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>mamonsu.memory.rss[max]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

    *RSS Memory Maximum Usage* shows amount of RSS memory allocated to Mamonsu in bytes.

### Triggers

1. **Mamonsu plugin errors on {HOSTNAME}. {ITEM.LASTVALUE}**  
    Shows Mamonsu last error message text. 

2. **Mamonsu nodata from {HOSTNAME}**  
    Triggers if there is no response from Mamonsu server more than 3 minutes.

3. **Mamonsu agent memory usage alert on {HOSTNAME}: {ITEM.LASTVALUE} bytes**  
    Triggers if *RSS Memory Maximum Usage* exceeds `max_memory_usage`.

## System metrics

### *nix

Default config:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;up_time = 300  

### Items

***Block Devices***  
*Block Devices metrics* use information from */proc/diskstats*.

1. **Block Devices Read Speed**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Block devices: read byte/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.disk.all_read_b[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

2. **Block Devices Read Requests**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Block devices: read requests</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.disk.all_read[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

3. **Block Devices Write Speed**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Block devices: write byte/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.disk.all_write_b[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

4. **Block Devices Write Requests**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Block devices: write requests</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.disk.all_write[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

***Load Average***  
*System Load Average Over 1 minute* uses information from */proc/loadavg* so no need for delta in Zabbix.

5. **System Load Average Over 1 Minute**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System load average over 1 minute</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.la[1]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

***Memory***  
*Memory metrics* use information from */proc/meminfo*.

6. **Active Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Active: Memory recently used</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[active]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

7. **Apps Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Apps: User-space applications</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[apps]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

    *Apps Memory* calculated as `MemTotal - (MemFree + Buffers + Cached + SwapCached + Slab + PageTables)`.  


8. **Buffers Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Buffers: Block device cache and dirty</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[buffers]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

9. **Cached Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Cached: Parked file data (file content) cache</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[cached]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

10. **Committed_AS Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Committed_AS: Total committed memory</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[committed]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

11. **MemFree Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Free: Wasted memory</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[unused]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

12. **Inactive Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Inactive: Memory not currently used</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[inactive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

13. **Mapped Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Mapped: All mmap()ed pages</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[mapped]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

14. **PageTables Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PageTables: Map bt virtual and physical</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[page_tables]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

15. **Slab Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Slab: Kernel used memory (inode cache)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[slab]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

16. **Swap Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Swap: Swap space used</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[swap]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

    *Swap Memory* calculated as `SwapTotal - SwapCached`.


17. **SwapCached Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>SwapCached: Fetched unmod yet swap pages</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[swap_cache]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

18. **VMallocUsed Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>VMallocUsed: vmaloc() allocated by kernel</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[vmalloc_used]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

***Open Files***  
*Open Files* uses information from /proc/sys/fs/file-nr.

19. **Open Files**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Opened files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.open_files[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

***Processes***  
*Processes metrics* use information from /proc/stat.

20. **Forkrate**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Processes: forkrate</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.processes[forkrate]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

    *Forkrate* shows number of processes created by calls to the fork() and clone() system calls.


21. **Blocked**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Processes: in state blocked</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.processes[blocked]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

22. **Running**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Processes: in state running</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.processes[running]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

***CPU***  
*CPU metrics* use information from /proc/stat.

23. **Nice**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent by nice(1)d programs</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[nice]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

24. **User**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent by normal programs and daemons</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[user]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

25. **System**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent by the kernel in system activities</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[system]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

26. **Softirq**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent handling batched interrupts</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[softirq]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

27. **Irq**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent handling interrupts</td></td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[irq]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

28. **Idle**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent Idle CPU time</td></td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[idle]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

29. **IOwait**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU time spent waiting for I/O operations</td></td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[iowait]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
    </table>

***Uptime***  
*Uptime* uses information from cat /proc/uptime.

30. **Uptime**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System up_time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.up_time[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Uptime</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>
    
    *Uptime* shows system uptime in units of time.

### Discovery Rules

1. **Block Device Discovery**  

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Block device {#BLOCKDEVICE}: read operations</td>
        <td>Block device {#BLOCKDEVICE}: write operations</td>
        <td>Block device {#BLOCKDEVICE}: read byte/s</td>
        <td>Block device {#BLOCKDEVICE}: write byte/s</td>
        <td>Block device {#BLOCKDEVICE}: utilization</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.disk.read[{#BLOCKDEVICE}]</td>
        <td>system.disk.write[{#BLOCKDEVICE}]</td>
        <td>system.disk.read_b[{#BLOCKDEVICE}]</td>
        <td>system.disk.write_b[{#BLOCKDEVICE}]</td>
        <td>system.disk.utilization[{#BLOCKDEVICE}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
        <td></td>
        <td>Bytes</td>
        <td>Bytes</td>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Block device overview: {#BLOCKDEVICE} byte/s</td>
        <td>Block device overview: {#BLOCKDEVICE} operations</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Block device {#BLOCKDEVICE}: read byte/s <br> Block device {#BLOCKDEVICE}: write byte/s <br> Block device {#BLOCKDEVICE}: utilization</td>
        <td>Block device {#BLOCKDEVICE}: read operations <br> Block device {#BLOCKDEVICE}: write operations <br> Block device {#BLOCKDEVICE}: utilization</td>
      </tr>
    </table>

2. **Net Iface Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Network device {#NETDEVICE}: RX bytes/s</td>
        <td>Network device {#NETDEVICE}: RX drops/s</td>
        <td>Network device {#NETDEVICE}: RX errors/s</td>
        <td>Network device {#NETDEVICE}: TX bytes/s</td>
        <td>Network device {#NETDEVICE}: TX drops/s</td>
        <td>Network device {#NETDEVICE}: TX errors/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.net.rx_bytes[{#NETDEVICE}]</td>
        <td>system.net.rx_drop[{#NETDEVICE}]</td>
        <td>system.net.rx_errs[{#NETDEVICE}]</td>
        <td>system.net.tx_bytes[{#NETDEVICE}]</td>
        <td>system.net.tx_drop[{#NETDEVICE}]</td>
        <td>system.net.tx_errs[{#NETDEVICE}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
        <td></td>
        <td></td>
        <td>Bytes</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Network device: {#NETDEVICE}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Network device {#NETDEVICE}: RX bytes/s <br> Network device {#NETDEVICE}: TX bytes/s</td>
      </tr>
    </table>

3. **VFS Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Mount point {#MOUNTPOINT}: free</td>
        <td>Mount point {#MOUNTPOINT}: free inodes in percent</td>
        <td>Mount point {#MOUNTPOINT}: free in percents</td>
        <td>Mount point {#MOUNTPOINT}: used</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.vfs.free[{#MOUNTPOINT}]</td>
        <td>system.vfs.percent_inode_free[{#MOUNTPOINT}]</td>
        <td>system.vfs.percent_free[{#MOUNTPOINT}]</td>
        <td>system.vfs.used[{#MOUNTPOINT}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
        <td>%</td>
        <td>%</td>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
        <td>As Is</td>
        <td>As Is</td>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Mount point overview: {#MOUNTPOINT}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Mount point {#MOUNTPOINT}: used	<br> Mount point {#MOUNTPOINT}: free</td>
      </tr>
    </table>

    Triggers:
    <table>
      <tr>
        <th>Name</th>
        <td>Free disk space less then 10% on mountpoint {#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})</td>
        <td>Free inode space less then 10% on mountpoint {#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})</td>
      </tr>
      <tr>
        <th>Expression</th>
        <td>Triggers if <i>Mount point {#MOUNTPOINT}: free in percent</i> exceeds vfs_inode_percent_free.</td>
        <td>Triggers if <i>Mount point {#MOUNTPOINT}: free inodes in percent</i> exceeds vfs_inode_percent_free.</td>
      </tr>
    </table>

4. **pg_probackup Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Pg_probackup dir {#BACKUPDIR}: error</td>
        <td>Pg_probackup dir {#BACKUPDIR}: size</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pg_probackup.dir.error[{#BACKUPDIR}]</td>
        <td>pg_probackup.dir.size[{#BACKUPDIR}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Text</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Pg_probackup: backup dir: {#BACKUPDIR} size</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Pg_probackup dir {#BACKUPDIR}: size</td>
      </tr>
    </table>

    Triggers:
    <table>
      <tr>
        <th>Name</th>
        <td>Error in pg_probackup dir {#BACKUPDIR} (hostname={HOSTNAME} value={ITEM.LASTVALUE})</td>
      </tr>
      <tr>
        <th>Expression</th>
        <td>Triggers if pg_probackup status is not OK.</td>
      </tr>
    </table>

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>Block devices: read/write bytes</td>
    <td>Block devices: read/write operations</td>
    <td>CPU time spent</td>
    <td>Memory overview</td>
    <td>Processes overview</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>Block devices: read byte/s <br> Block devices: write byte/s</td>
    <td>Block devices: read requests <br> Block devices: write requests</td>
    <td>CPU time spent by normal programs and daemons <br> CPU time spent by nice(1)d programs <br> CPU time spent by the kernel in system activities <br> CPU time spent Idle CPU time <br> CPU time spent waiting for I/O operations	avg <br> CPU time spent handling interrupts	<br> CPU time spent handling batched interrupts</td>
    <td>Apps: User-space applications <br> Buffers: Block device cache and dirty <br> Swap: Swap space used	<br> Cached: Parked file data (file content) cache <br> Free: Wasted memory	<br> Slab: Kernel used memory (inode cache) <br> SwapCached: Fetched unmod yet swap pages <br> PageTables: Map bt virtual and physical <br> VMallocUsed: vmaloc() allocated by kernel <br> Committed_AS: Total committed memory <br> Mapped: All mmap()ed pages <br> Active: Memory recently used <br> Inactive: Memory not currently used</td>
    <td>Processes: in state running	<br> Processes: in state blocked <br> Processes: forkrate</td>
  </tr>
</table>

### Triggers

1. **Process fork-rate to frequently on {HOSTNAME}**  
    Triggers if *Processes: forkrate* greater than 500.

2. **System was restarted on {HOSTNAME} (up_time={ITEM.LASTVALUE})**  
    Triggers if *System up_time* fails `up_time`.

### Windows

### Items

***Memory***

1. **Cached**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Memory cached</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[cache]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

2. **Available**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Memory available</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[available]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

3. **Free**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Memory free</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[free]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

***CPU***  

1. **User time**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU User time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[user_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

2. **Idle time**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU Idle time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[idle_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

3. **Privileged Time**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>CPU Privileged time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.cpu[privileged_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

***Network***  

1. **Output Queue Length**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Network Output Queue Length</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.network[total_output_queue]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

2. **Bytes Total**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>Network Bytes Total</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.network[total_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

### Discovery Rules

1. **Logical Disks Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Logical device {#LOGICALDEVICE}: read op/sec</td>
        <td>Logical device {#LOGICALDEVICE}: write op/sec</td>
        <td>Logical device {#LOGICALDEVICE}: queue</td>
        <td>Logical device {#LOGICALDEVICE}: idle time (%)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.disk.read[{#LOGICALDEVICE}]</td>
        <td>system.disk.write[{#LOGICALDEVICE}]</td>
        <td>system.disk.queue_avg[{#LOGICALDEVICE}]</td>
        <td>system.disk.idle[{#LOGICALDEVICE}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
        <td></td>
        <td></td>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
        <td>Speed Per Second</td>
        <td>As Is</td>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Logical devices overview: {#LOGICALDEVICE}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Logical device {#LOGICALDEVICE}: read op/sec <br> Logical device {#LOGICALDEVICE}: write op/sec <br> Logical device {#LOGICALDEVICE}: queue</td>
      </tr>
    </table>

## PostgreSQL metrics

### Archiving

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_count_files = 2

### Items

*Archiving metrics* use information from `pg_stat_archiver`.

1. **Archived Files**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL archive command count archived files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.archive_command[archived_files]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Archived Files* maps `archived_count`.


2. **Attempts To Archive Files**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL archive command count attempts to archive files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.archive_command[failed_trying_to_archive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Attempts To Archive Files* maps `failed_count`.


3. **Files Need To Archive**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL archive command count files in archive_status need to archive</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.archive_command[count_files_to_archive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Files Need To Archive* is calculated as difference between current WAL number and last archived WAL number. You can find SQL-query that calculates this metric in plugin source [code](../mamonsu/plugins/pgsql/archive_command.py).


4. **Size Of Files Need To Archive**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL archive command size of files need to archive</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.archive_command[size_files_to_archive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Size Of Files Need To Archive* is calculated as difference between current WAL number and last archived WAL number multiplied by `wal_segment_size`. You can find SQL-query that calculates this metric in plugin source [code](../mamonsu/plugins/pgsql/archive_command.py).

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL archive command  archive status </td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL archive command count files in archive_status need to archive <br> PostgreSQL archive command count archived files <br> PostgreSQL archive command count attempts to archive files</td>
  </tr>
</table>

### Triggers

1. **PostgreSQL count files in ./archive_status on {HOSTNAME} more than 2**  
    Triggers if *PostgreSQL archive command count files in archive_status need to archive* exceeds `max_count_files`.

## Autovacuum

### Items

*Autovacuum metrics* use information from `pg_stat_activity`.

1. **Autovacuum Workers**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: count of autovacuum workers</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.autovacumm.count[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Autovacuum Workers* calculates as summa of avtovacuum queries with not idle state.

## Background Writer

### Items

*Background Writer metrics* use information from `pg_stat_bgwriter`.  

1. **Buffers Allocated**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: buffers allocated</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.bgwriter[buffers_alloc]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Buffers Allocated* maps `buffers_alloc`.


2. **Buffers Written**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: buffers written</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.bgwriter[buffers_clean]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Buffers Written* maps `buffers_clean`.


3. **Buffers Written Directly By a Backend**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: buffers written directly by a backend</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.bgwriter[buffers_backend]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Buffers Written Directly By a Backend* maps `buffers_backend`.


4. **Buffers Written During Checkpoints**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: buffers written during checkpoints</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.bgwriter[buffers_checkpoint]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Buffers Written During Checkpoints* maps `buffers_checkpoint`.


5. **Bgwriter Stopped a Cleaning Scan**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: number of bgwriter stopped by max write count</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.bgwriter[maxwritten_clean]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Bgwriter Stopped a Cleaning Scan* maps `maxwritten_clean`.


6. **Backend Executes Its Own Fsync Call**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: times a backend execute its own fsync</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.bgwriter[buffers_backend_fsync]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Backend Executes Its Own Fsync Call* maps `buffers_backend_fsync`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL bgwriter buffers</td>
    <td>PostgreSQL bgwriter write/sync</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL bgwriter: buffers written during checkpoints <br> PostgreSQL bgwriter: buffers written <br> PostgreSQL bgwriter: buffers written directly by a backend <br> PostgreSQL bgwriter: buffers allocated</td>
    <td>PostgreSQL bgwriter: number of bgwriter stopped by max write count <br> PostgreSQL bgwriter: times a backend execute its own fsync</td>
  </tr>
</table>

### Blocks

### Items

*Blocks metrics* use information from `pg_stat_database`.

1. **Blocks Hit**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL blocks: hit</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.blocks[hit]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Blocks Hit* maps `blks_hit`.


2. **Blocks Read**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL blocks: read</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.blocks[read]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Blocks Read* maps `blks_read`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL instance: rate</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL transactions: committed <br> PostgreSQL blocks: hit <br> PostgreSQL blocks: read</td>
  </tr>
</table>

### Checkpoints

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_checkpoint_by_wal_in_hour = 12

### Items

*Checkpoints metrics* use information from `pg_stat_bgwriter`.

1. **Checkpoints Sync Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL checkpoint: sync time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.checkpoint[checkpoint_sync_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>ms</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Checkpoints Sync Time* maps `checkpoint_sync_time`.


2. **Checkpoints Write Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL checkpoint: write time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.checkpoint[write_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>ms</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Checkpoints Write Time* maps `checkpoint_write_time`.


3. **Scheduled Checkpoints**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL checkpoints: by timeout (in hour)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.checkpoint[count_timed]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Scheduled Checkpoints* maps `checkpoints_timed`.


4. **Requested Checkpoints**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL checkpoints: by wal (in hour)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.checkpoint[count_wal]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Requested Checkpoints* maps `checkpoints_req`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL checkpoints</td>
    <td>PostgreSQL checkpoints write/sync</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL checkpoints: by timeout (in hour) <br> PostgreSQL checkpoints: by wal (in hour)</td>
    <td>PostgreSQL checkpoint: write time <br> PostgreSQL checkpoint: sync time</td>
  </tr>
</table>

### Triggers

1. **PostgreSQL required checkpoints occurs to frequently on {HOSTNAME}**  
    Triggers if *PostgreSQL checkpoints: by wal (in hour)* exceeds `max_checkpoint_by_wal_in_hour`.

### Connections

Default config:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;percent_connections_tr = 90

### Items

*Connections metrics* use information from `pg_stat_activity`.

1. **Max Connections**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: max connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[max_connections]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Max Connections* maps `pg_settings max_connections`.


2. **Active**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of active connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[active]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Active* calculates as summa of connections from `pg_stat_activity` with state `active`.


3. **Disabled**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of disabled</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[disabled]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Disabled* calculates as summa of connections from `pg_stat_activity` with state `disabled`.


4. **Fastpath Function Call**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of fastpath function call</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[fastpath_function_call]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Fastpath Function Call* calculates as summa of connections from `pg_stat_activity` with state `fastpath function call`.


5. **Idle**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of idle connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[idle]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Idle* calculates as summa of connections from `pg_stat_activity` with state `idle`.


6. **Idle in Transaction**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of idle in transaction connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[idle_in_transaction]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Idle in Transaction* calculates as summa of connections from `pg_stat_activity` with state `idle in transaction`.


7. **Idle in Transaction (aborted)**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of idle in transaction (aborted)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[idle_in_transaction_aborted]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Idle in Transaction (aborted)* calculates as summa of connections from `pg_stat_activity` with state `idle in transaction (aborted)`.


8. **Total**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of total connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[total]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Total* calculates as summa of all connections from `pg_stat_activity` with not null state.


9. **Waiting**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of waiting connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[waiting]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Waiting* calculates as summa of all connections from `pg_stat_activity` with not null state and wait_event_type.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL connections</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL: number of active connections <br> PostgreSQL: number of idle connections <br> PostgreSQL: number of idle in transaction connections <br> PostgreSQL: number of idle in transaction (aborted) <br> PostgreSQL: number of fastpath function call <br> PostgreSQL: number of disabled <br> PostgreSQL: number of total connections <br> PostgreSQL: number of waiting connections <br> PostgreSQL: max connections</td>
  </tr>
</table>

### Triggers

1. **PostgreSQL many connections on {HOSTNAME} (total connections more than 90% max connections)**  
    Triggers if connections count exceeds `percent_connections_tr`.

### Databases

### Discovery Rules

1. **Database Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Count of bloating tables in database: {#DATABASE}</td>
        <td>Database {#DATABASE}: size</td>
        <td>Max age (datfrozenxid) in: {#DATABASE}</td>
        <td>Count of invalid indexes in database: {#DATABASE}</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.database.bloating_tables[{#DATABASE}]</td>
        <td>pgsql.database.size[{#DATABASE}]</td>
        <td>pgsql.database.max_age[{#DATABASE}]</td>
        <td>pgsql.database.invalid_indexes[{#DATABASE}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
        <td>Bytes</td>
        <td></td>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
        <td>As Is</td>
        <td>As Is</td>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Database: {#DATABASE} size</td>
        <td>Database bloating overview: {#DATABASE}</td>
        <td>Database max age overview: {#DATABASE}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Database {#DATABASE}: size</td>
        <td>Count of bloating tables in database: {#DATABASE} <br> PostgreSQL: count of autovacuum workers</td>
        <td>Max age (datfrozenxid) in: {#DATABASE} <br> PostgreSQL: count of autovacuum workers</td>
      </tr>
    </table>

### Events

### Items

*Events metrics* use information from `pg_stat_database`.

1. **Conflicts**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL event: conflicts</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.events[conflicts]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Conflicts* maps `conflicts`.


2. **Deadlocks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL event: deadlocks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.events[deadlocks]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Deadlocks* maps `deadlocks`.


3. **Rollbacks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL event: rollbacks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.events[xact_rollback]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>   <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Rollbacks* maps `xact_rollback`.


4. **Checksum Failures**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL event: checksum_failures</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.events[checksum_failures]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>12+</td>
      </tr>
    </table>

    *Checksum Failures* maps `checksum_failures`.

### Graphs
<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL instance: events</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL event: conflicts	<br> PostgreSQL event: deadlocks <br> PostgreSQL event: rollbacks <br> PostgreSQL event: checksum_failures</td>
  </tr>
</table>

### Health

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;uptime = 600  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cache = 80

### Items


1. **Ping**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: ping</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.ping[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>ms</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Ping* calculates as difference between *ping query* start time and time of receiving *ping query* result.


2. **Cache Hit Ratio**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: cache hit ratio</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cache[hit]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Cache Hit Ratio* calculates as ratio between last value of `Blocks hit` and summa of last values of `Blocks hit` and `Blocks read`.


3. **Service Uptime**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: service uptime</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.uptime[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Unixtime</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Service Uptime* maps `pg_postmaster_start_time`.

### Triggers

1. **PostgreSQL cache hit ratio too low on {HOSTNAME} ({ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL: cache hit ratio* fails `cache`.

2. **PostgreSQL service was restarted on {HOSTNAME} (uptime={ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL: service uptime* fails `uptime`.

3. **PostgreSQL no ping from PostgreSQL for 3 minutes {HOSTNAME}**  
    Triggers if there is no data from *PostgreSQL: ping* more than 3 minutes.

### Memory Leak

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;private_anon_mem_threshold = 1 Gb  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval = 60

### Items

1. **private_anon_mem_threshold Exceeding Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of pids which private anonymous memory exceeds private_anon_mem_threshold</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.memory_leak_diagnostic.count_diff[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

2. **private_anon_mem_threshold Exceeding Messages Text**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of pids which private anonymous memory exceeds private_anon_mem_threshold, text of message</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.memory_leak_diagnostic.msg_text[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Text</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

### Triggers
1. **PostgreSQL: number of pids which private anonymous memory exceeds private_anon_mem_threshold on {HOSTNAME}. {ITEM.LASTVALUE}**  
    Triggers if there is memory leak errors. Shows memory leak error messages text. 

### pg_buffercache

### Items

*pg_buffercache metrics* use information from `pg_buffercache`.

1. **Shared Buffer Size**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: shared buffer size</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.buffers[size]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Shared Buffer Size* calculates as count of all rows in pg_buffercache multiplied by `block_size`.


2. **Shared Buffer Twice Used Size**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: shared buffer twice used size</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.buffers[twice_used]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Shared Buffer Twice Used Size* calculates as count of all rows in pg_buffercache where usagecount greater than 1 multiplied by `block_size`.


3. **Shared Buffer Dirty Size**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: shared buffer dirty size</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.buffers[dirty]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Shared Buffer Dirty Size* calculates as count of all isdirty rows in pg_buffercache multiplied by `block_size`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL: shared buffer</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL: shared buffer size <br> PostgreSQL: shared buffer twice used size <br> PostgreSQL: shared buffer dirty size</td>
  </tr>
</table>

### pg_locks

### Items

*pg_locks metrics* use information from `pg_locks`.

1. **Access Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX, CLUSTER, VACUUM FULL, LOCK TABLE</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[accessexclusive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Access Exclusive* calculates as summa of locks from `pg_locks` with mode `Access Exclusive`.


2. **Access Share**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: Read only queries</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[accessshare]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Access Share* calculates as summa of locks from `pg_locks` with mode `Access Share`.


3. **Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: Locks from application or some operation on system catalogs</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[exclusive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Exclusive* calculates as summa of locks from `pg_locks` with mode `Exclusive`.


4. **Row Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: Write queries</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[rowexclusive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Row Exclusive* calculates as summa of locks from `pg_locks` with mode `Row Exclusive`.


5. **Row Share**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: SELECT FOR SHARE and SELECT FOR UPDATE</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[rowshare]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Row Share* calculates as summa of locks from `pg_locks` with mode `Row Share`.


6. **Share Row Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: Locks from application</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[sharerowexclusive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Share Row Exclusive* calculates as summa of locks from `pg_locks` with mode `Share Row Exclusive`.


7. **Share Update Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[shareupdateexclusive]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Share Update Exclusive* calculates as summa of locks from `pg_locks` with mode `Share Update Exclusive`.


8. **Share**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL locks: CREATE INDEX</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.pg_locks[share]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Share* calculates as summa of locks from `pg_locks` with mode `Share`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL locks sampling</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL locks: Read only queries <br> PostgreSQL locks: SELECT FOR SHARE and SELECT FOR UPDATE <br> PostgreSQL locks: Write queries <br> PostgreSQL locks: VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY <br> PostgreSQL locks: CREATE INDEX <br> PostgreSQL locks: Locks from application <br> PostgreSQL locks: Locks from application or some operation on system catalogs <br> PostgreSQL locks: ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX, CLUSTER, VACUUM FULL, LOCK TABLE</td>
  </tr>
</table>

### pg_stat_statements

### Items

*pg_stat_statements metrics* use information from `pg_stat_statements` and `pg_stat_statements_info`.

1. **Amount of WAL Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: amount of wal files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[wal_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Amount of WAL Files* maps `wal_bytes`.


2. **Amount of WAL Records**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: amount of wal records</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[wal_records]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Amount of WAL Records* maps `wal_records`.


3. **Dirty Bytes**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: dirty bytes/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[dirty_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Dirty Bytes* calculates as summa of `shared_blks_dirtied` and `local_blks_dirtied`.


4. **WAL FPI**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: full page writes</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[wal_fpi]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *WAL FPI* maps `wal_fpi`.


5. **Read IO Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: read io time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[read_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Read IO Time* maps `blk_read_time`


6. **Write IO Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: write io time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[write_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Write IO Time* maps `blk_write_time`


7. **Other Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: other (mostly cpu) time</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[other_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Other Time* calculates as `total_time - blk_read_time - blk_write_time`.


8. **Read Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: read bytes/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[read_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Read Speed* calculates as `shared_blks_read`, `local_blks_read` and `temp_blks_read`.


9. **Write Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: write bytes/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat[write_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
       <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Write Speed* calculates as summa of `shared_blks_written` and `local_blks_written`.


10. **Last Statistic Reset**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: last statistics reset</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat_info[stats_reset]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Unixtime</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *Last Statistic Reset* maps `stats_reset`.


11. **pg_stat_statements.max Exceeding Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL statements: the number of times the pg_stat_statements.max was exceeded</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.stat_info[dealloc]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
       <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *pg_stat_statements.max Exceeding Count* maps `dealloc`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL statements: bytes</td>
    <td>PostgreSQL statements: spend time</td>
    <td>PostgreSQL statements: wal statistics</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL statements: read bytes/s	<br> PostgreSQL statements: write bytes/s <br> PostgreSQL statements: dirty bytes/s</td>
    <td>PostgreSQL statements: read io time <br> PostgreSQL statements: write io time <br> PostgreSQL statements: other (mostly cpu) time</td>
    <td>PostgreSQL statements: amount of wal files <br> PostgreSQL statements: amount of wal records <br> PostgreSQL statements: full page writes</td>
  </tr>
</table>

### Prepared Transactions

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_prepared_transaction_time = 18000

### Items

*Prepared Transactions metrics* use information from `pg_prepared_xacts`.   

1. **Prepared Transactions Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: number of prepared transactions</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.prepared.count</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Prepared Transactions Count* calculates as summa of all rows in `pg_prepared_xacts`.


2. **Oldest Prepared Transaction Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: oldest prepared transaction time in sec</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.prepared.oldest</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Oldest Prepared Transaction Time* calculates as `max(now() - prepared)`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL prepared transaction</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL: number of prepared transactions	<br> PostgreSQL: oldest prepared transaction time in sec</td>
  </tr>
</table>

### Triggers

1. **PostgreSQL prepared transaction is too old on {HOSTNAME}**  
    Triggers if *PostgreSQL: oldest prepared transaction time in sec* exceeds `max_prepared_transaction_time`.

### Relations

### Discovery Rules

1. **Relation Size Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Relation size: {#RELATIONNAME}</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.relation.size[{#RELATIONNAME}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL relation size: {#RELATIONNAME}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Relation size: {#RELATIONNAME}</td>
      </tr>
    </table>

### Replication

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lag_more_than_in_sec = 300

### Items

*Replication metrics* use information from `pg_replication_slots`.

1. **Non-active Replication Slots**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: count non-active replication slots</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.replication.non_active_slots[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Non-active Replication Slots* calculates as count of slots with `false` active status.


2. **Streaming Replication Lag**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: streaming replication lag</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.replication_lag[sec]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Streaming Replication Lag* calculates as difference between now and `pg_last_xact_replay_timestamp`.

### Discovery Rules

1. **Replication Lag Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Delta of total lag for {#APPLICATION_NAME}</td>
        <td>Time elapsed between flushing recent WAL locally and receiving notification that this standby server {#APPLICATION_NAME} has written, flushed and applied</td>
        <td>Time elapsed between flushing recent WAL locally and receiving notification that this standby server {#APPLICATION_NAME} has written and flushed it</td>
        <td>Time elapsed between flushing recent WAL locally and receiving notification that this standby server {#APPLICATION_NAME} has written it</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.replication.total_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.replay_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.flush_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.write_lag[{#APPLICATION_NAME}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
        <td>Text</td>
        <td>Text</td>
        <td>Text</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
        <td>As Is</td>
        <td>As Is</td>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Delta of total lag for {#APPLICATION_NAME}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Delta of total lag for {#APPLICATION_NAME}</td>
      </tr>
    </table>

### Triggers

1. **PostgreSQL number of non-active replication slots on {HOSTNAME} (value={ITEM.LASTVALUE})**  

2. **PostgreSQL streaming lag too high on {HOSTNAME} (value={ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL: streaming replication lag* exceeds `lag_more_than_in_sec`.

### Temp Files

### Items

*Temp Files metrics* use information from `pg_stat_database`.  

1. **Temp Bytes**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL temp: bytes written</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.temp[bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Temp Bytes* maps `temp_bytes`.


2. **Temp Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL temp: files created</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.temp[files]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Simple Change</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Temp Files* maps `temp_files`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL instance: temp files</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL temp: bytes written <br> PostgreSQL temp: files created</td>
  </tr>
</table>

### Transactions

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_xid_age = 18000000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_transaction_time = 18000

### Items

1. **Committed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL transactions: committed</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.transactions[committed]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Committed* maps `xact_commit` from `pg_stat_database`.


2. **Oldest Transaction Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: oldest transaction running time in sec</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.oldest[transaction_time]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
   *Oldest Transaction Time* calculates based on data from `pg_stat_activity`. You can find SQL-query that calculates this metric in plugin source [code](../mamonsu/plugins/pgsql/oldest.py).


3. **Oldest XID Age**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: age of oldest xid</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.oldest[xid_age]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
   *Oldest XID Age* calculates based on data from `pg_stat_activity`. You can find SQL-query that calculates this metric in plugin source [code](../mamonsu/plugins/pgsql/oldest.py).


### Triggers

1. **PostgreSQL oldest xid is too big on {HOSTNAME}**  
    Triggers if *PostgreSQL: age of oldest xid* exceeds `max_xid_age`.

2. **PostgreSQL query running is too old on {HOSTNAME}**  
    Triggers if *PostgreSQL: oldest transaction running time in sec* exceeds `max_transaction_time`.

### Tuples

### Items

*Tuples metrics* use information from `pg_stat_database`.

1. **Deleted**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL tuples: deleted</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.tuples[deleted]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Deleted* maps `tup_deleted`.


2. **Fetched**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL tuples: fetched</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.tuples[fetched]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Fetched* maps `tup_fetched`.


3. **Inserted**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL tuples: inserted</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.tuples[inserted]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Inserted* maps `tup_inserted`.


4. **Returned**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL tuples: returned</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.tuples[returned]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Returned* maps `tup_returned`.


5. **Updated**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL tuples: updated</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.tuples[updated]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Updated* maps `tup_updated`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL instance: tuples</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL tuples: deleted <br> PostgreSQL tuples: fetched <br> PostgreSQL tuples: inserted	avg <br> PostgreSQL tuples: returned <br> PostgreSQL tuples: updated</td>
  </tr>
</table>

### WAL

### Items

*WAL metrics* use information from `pg_stat_wal`.  

1. **WAL Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: count of xlog files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.count[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *WAL count* calculates as count of WAL files in `pg_wal` directory via `pg_ls_dir()`.


2. **WAL Write Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal write speed</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.write[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *WAL Write Speed* calculates as difference between current WAL file and `0/00000000`.


3. **WAL Buffers Full**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal buffers full</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.buffers_full</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *WAL Buffers Full* maps `wal_buffers_full`.


4. **WAL FPI Generated**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal full page images generated</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.fpi.count[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Seconds</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *WAL FPI Generated* maps `wal_fpi`.


5. **WAL Records Generated**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal records generated</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.records.count[]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Seconds</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *WAL Records Generated* maps `wal_records`.

6. **WAL Sync Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal sync time (ms)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.sync_time</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>ms</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *WAL Sync Time* maps `wal_sync_time`.


7. **WAL Write Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal write time (ms)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.write_time</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *WAL Write Time* maps `wal_write_time`.


8. **WAL Sync Duty**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL: wal sync duty (%)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.wal.sync_duty</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>%</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>14+</td>
      </tr>
    </table>
   
    *WAL Sync Duty* calculates as change of `wal_sync_time` per Mamonsu interval.

## Postgres Pro metrics

### Compressed File System

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;force_enable = False

### Items

*Compressed File System metrics* use information from `cfs*` functions.

1. **Compressed Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL cfs compression: compressed files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.activity[compressed_files]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Compressed Files* maps `cfs_gc_activity_processed_files()`.


2. **Scanned Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL cfs compression: scanned files</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.activity[scanned_files]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>
   
    *Scanned Files* maps `cfs_gc_activity_scanned_files()`.


3. **Current Ratio**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL cfs compression: current ratio</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.activity[current_compress_ratio]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

4. **Total Ratio**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL cfs compression: total ratio</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.activity[total_compress_ratio]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

5. **Scanned Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL cfs compression: scanned byte/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.activity[scanned_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Scanned Speed* maps `cfs_gc_activity_processed_pages()`.


6. **Written Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL cfs compression: written byte/s</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.activity[written_bytes]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td>byte/s</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

    *Written Speed* maps `cfs_gc_activity_processed_bytes()`.

### Discovery Rules

1. **Compressed Relations Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>Relation {#COMPRESSED_RELATION}: compress ratio</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.cfs.compress_ratio[{#COMPRESSED_RELATION}]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
      </tr>
    </table>

    Graphs:
    <table>
      <tr>
        <th>Name</th>
        <td>Relation {#COMPRESSED_RELATION}: compress ratio</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>Relation {#COMPRESSED_RELATION}: compress ratio</td>
      </tr>
    </table>

### pg_wait_sampling

### Items

*pg_wait_sampling metrics* use information from `pg_wait_sampling_profile`.  

***Buffer Locks***
1. **Buffer Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: Buffer locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.all_lock[buffer]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

***Heavyweight Locks***
1. **Heavyweight Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: Heavyweight locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.all_lock[hwlock]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

2. **Advisory User Lock**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: advisory user lock</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[advisory]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

3. **Extend a Relation**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: extend a relation</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[extend]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

4. **Lock On a Relation**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: lock on a relation</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[relation]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

5. **Lock On a Tuple**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: lock on a tuple</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[tuple]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

6. **Lock On Database Object**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: lock on database object</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[object]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

7. **Lock On Page**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: lock on page</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[page]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

8. **Speculative Insertion Lock**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: speculative insertion lock</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[speculative_token]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

9. **Transaction to Finish**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: transaction to finish</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[transactionid]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

10. **Userlock**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: userlock</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[userlock]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

11. **Virtual XID Lock**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: virtual xid lock</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.hwlock[virtualxid]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

***Lightweight Locks***
1. **Lightweight Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: Lightweight locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.all_lock[lwlock]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

2. **Buffer Operations**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: Buffer operations</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[buffer]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

3. **CLOG Access**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: CLOG access</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[clog]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

4. **Replication Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: Replication Locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[replication]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

5. **WAL Access**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: WAL access</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[wal]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

6. **XID Access**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: XID access</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[xid]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

7. **Other Operations**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL waits: Other operations</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[other]</td>
      </tr>
      <tr>
        <th>Type</th>
        <td>Numeric (float)</td>
      </tr>
      <tr>
        <th>Units</th>
        <td></td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>Speed Per Second</td>
      </tr>
      <tr>
        <th>Supported Version</th>
        <td>9.5+</td>
      </tr>
    </table>

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL waits: Heavyweight locks</td>
    <td>PostgreSQL waits: Lightweight locks</td>
    <td>PostgreSQL waits: Locks by type</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL waits: lock on a relation <br> PostgreSQL waits: extend a relation <br> PostgreSQL waits: lock on page <br> PostgreSQL waits: lock on a tuple <br> PostgreSQL waits: transaction to finish <br> PostgreSQL waits: virtual xid lock <br> PostgreSQL waits: speculative insertion lock	<br> PostgreSQL waits: lock on database object <br> PostgreSQL waits: userlock <br> PostgreSQL waits: advisory user lock</td>
    <td>PostgreSQL waits: XID access <br> PostgreSQL waits: WAL access <br> PostgreSQL waits: CLOG access <br> PostgreSQL waits: Replication Locks <br> PostgreSQL waits: Buffer operations	<br> PostgreSQL waits: Other operations</td>
    <td>PostgreSQL waits: Lightweight locks <br> PostgreSQL waits: Heavyweight locks <br> PostgreSQL waits: Buffer locks</td>
  </tr>
</table>
