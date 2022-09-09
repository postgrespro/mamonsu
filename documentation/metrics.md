# mamonsu: metrics

**Metrics:**
- [mamonsu health metrics](#mamonsu-health-metrics)
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
  - [Statements](#statements)
    - [Items](#items-14)
    - [Graphs](#graphs-9)
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
  - [Wait Sampling](#wait-sampling)
    - [Items](#items-22)
    - [Graphs](#graphs-13)
    
## mamonsu Health metrics

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_memory_usage = 40 Mb

### Items

- **Plugin Errors**

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

    *Plugin Errors* collects _mamonsu_ error messages. It might be PostgreSQL extensions errors, rights errors, etc.


- **Plugin Health**

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
   
    *Plugin Health* indicates that _mamonsu_ is running.


- **RSS Memory Maximum Usage (for UNIX only)**

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

    *RSS Memory Maximum Usage* shows amount of RSS memory allocated to _mamonsu_ in bytes.

### Triggers

- **Mamonsu plugin errors on {HOSTNAME}. {ITEM.LASTVALUE}**  
    Shows _mamonsu_ last error message text. 

- **Mamonsu nodata from {HOSTNAME}**  
    Triggers if there is no response from _mamonsu_ server more than 3 minutes.

- **Mamonsu agent memory usage alert on {HOSTNAME}: {ITEM.LASTVALUE} bytes**  
    Triggers if *RSS Memory Maximum Usage* exceeds `max_memory_usage`.

## System metrics

### *nix

Default config:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;up_time = 300  

### Items

***Block Devices***  
*Block Devices metrics* use information from */proc/diskstats*.

- **Block Devices Read Speed**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Block Devices Read byte/s</td>
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

- **Block Devices Read Requests**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Block Devices Read Requests</td>
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

- **Block Devices Write Speed**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Block Devices Write byte/s</td>
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

- **Block Devices Write Requests**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Block Devices Write Requests</td>
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

- **System Load Average Over 1 Minute**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Load Average Over 1 Minute</td>
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

- **Active Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Active - Memory Recently Used</td>
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

- **Used Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Used - User-Space Applications</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.memory[used]</td>
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

    *Used Memory* calculated as `MemTotal - (MemFree + Buffers + Cached + SwapCached + Slab + PageTables)`.  


- **Buffers Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Buffers - Block Device Cache and Dirty</td>
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

- **Cached Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Cached - Parked File Data (file content) Cache</td>
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

- **Committed_AS Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Committed AS - Total Committed Memory</td>
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

- **Unused Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Unused - Wasted Memory</td>
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

- **Available Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Available - Free Memory</td>
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

- **Inactive Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Inactive - Memory Not Currently Used</td>
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

- **Mapped Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Mapped - All mmap()ed Pages</td>
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

- **PageTables Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: PageTables - Map bt Virtual and Physical</td>
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

- **Slab Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Slab - Kernel Used Memory (inode cache)</td>
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

- **Swap Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Swap - Swap Space Used</td>
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


- **SwapCached Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: SwapCached - Fetched unmod Yet Swap Pages</td>
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

- **VMallocUsed Memory**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: VMallocUsed - vmaloc() Allocated by Kernel</td>
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

- **Opened Files**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Opened Files</td>
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

- **Forkrate**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Processes Forkrate</td>
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


- **Blocked**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Processes in State Blocked</td>
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

- **Running**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Processes in State Running</td>
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

- **Nice**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent by nice(1)d Programs</td>
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

- **User**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent by Normal Programs and Daemons</td>
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

- **System**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent by the Kernel in System Activities</td>
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

- **Softirq**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent Handling Batched Interrupts</td>
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

- **Irq**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent Handling Interrupts</td></td>
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

- **Idle**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent Idle</td></td>
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

- **IOwait**

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Time Spent Waiting for I/O Operations</td></td>
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

- **Uptime**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Uptime</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>system.uptime[]</td>
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

- **System: Block Devices Discovery**  

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>System: Block Device {#BLOCKDEVICE} Read Operations</td>
        <td>System: Block Device {#BLOCKDEVICE} Write Operations</td>
        <td>System: Block Device {#BLOCKDEVICE} Read byte/s</td>
        <td>System: Block Device {#BLOCKDEVICE} Write byte/s</td>
        <td>System: Block Device {#BLOCKDEVICE} Utilization</td>
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
        <td>System: Block Device Overview {#BLOCKDEVICE} byte/s</td>
        <td>System: Block Device Overview {#BLOCKDEVICE} operations</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>System: Block Device {#BLOCKDEVICE} Read byte/s <br> System: Block Device {#BLOCKDEVICE} Write byte/s <br> System: Block Device {#BLOCKDEVICE} Utilization</td>
        <td>System: Block Device {#BLOCKDEVICE} Read Operations <br> System: Block Device {#BLOCKDEVICE} Write Operations <br> System: Block Device {#BLOCKDEVICE} Utilization</td>
      </tr>
    </table>

- **Net Iface Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>System: Network Device {#NETDEVICE} RX bytes/s</td>
        <td>System: Network Device {#NETDEVICE} RX drops/s</td>
        <td>System: Network Device {#NETDEVICE} RX errors/s</td>
        <td>System: Network Device {#NETDEVICE} TX bytes/s</td>
        <td>System: Network Device {#NETDEVICE} TX drops/s</td>
        <td>System: Network Device {#NETDEVICE} TX errors/s</td>
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
        <td>System: Network Device {#NETDEVICE}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>System: Network Device {#NETDEVICE} RX bytes/s <br> System: Network Device {#NETDEVICE} TX bytes/s</td>
      </tr>
    </table>

- **VFS Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>System: Mount Point {#MOUNTPOINT} Free</td>
        <td>System: Mount Point {#MOUNTPOINT} Free Inodes in Percent</td>
        <td>System: Mount Point {#MOUNTPOINT} Free in Percents</td>
        <td>System: Mount Point {#MOUNTPOINT} Used</td>
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
        <td>System: Mount Point Overview {#MOUNTPOINT}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>System: Mount Point {#MOUNTPOINT} Used	<br> System: Mount Point {#MOUNTPOINT} Free</td>
      </tr>
    </table>

    Triggers:
    <table>
      <tr>
        <th>Name</th>
        <td>Free disk space less than 10% on mountpoint {#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})</td>
        <td>Free inode space less than 10% on mountpoint {#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})</td>
      </tr>
      <tr>
        <th>Expression</th>
        <td>Triggers if <i>System: Mount Point {#MOUNTPOINT}: Free in Percent</i> exceeds vfs_inode_percent_free.</td>
        <td>Triggers if <i>System: Mount Point {#MOUNTPOINT}: Free Inodes in Percent</i> exceeds vfs_inode_percent_free.</td>
      </tr>
    </table>

- **pg_probackup Discovery**

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
    <td>System: Block Devices Read/Write Bytes</td>
    <td>System: Block Devices Read/Write Operations</td>
    <td>System: CPU Time Spent</td>
    <td>System: Server Memory Detailed Overview</td>
    <td>System: Server Free/Used Memory Overview</td>
    <td>System: Processes Overview</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>System: Block Devices Read byte/s <br> System: Block Devices Write byte/s</td>
    <td>System: Block Devices Read Requests <br> System: Block Devices Write Requests</td>
    <td>System: CPU Time Spent by Normal Programs and Daemons <br> System: CPU Time Spent by nice(1)d Programs <br> System: CPU Time Spent by the Kernel in System Activities <br> System: CPU Time Spent Idle <br> System: CPU Time Spent Waiting for I/O Operations <br> System: CPU Time Spent Handling Interrupts <br> System: CPU Time Spent Handling Batched Interrupts </td>
    <td>System: Available - Free Memory <br> System: Cached - Parked File Data (file content) Cache	 <br> System: Total - All Memory <br> System: Used - User-Space Applications</td>
    <td>f</td>
    <td>Processes: in state running	<br> Processes: in state blocked <br> Processes: forkrate</td>
  </tr>
</table>

### Triggers

- **Process fork-rate too frequently on {HOSTNAME}**  
    Triggers if *Processes: forkrate* greater than 500.

- **System was restarted on {HOSTNAME} (uptime={ITEM.LASTVALUE})**  
    Triggers if *System up_time* fails `up_time`.

### Windows

### Items

***Memory***

- **Cached**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Memory Cached</td>
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

- **Available**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Memory Available</td>
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

- **Free**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Memory Free</td>
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

- **User time**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU User Time</td>
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

- **Idle time**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Idle Time</td>
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

- **Privileged Time**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: CPU Privileged Time</td>
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

- **Output Queue Length**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Network Output Queue Length</td>
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

- **Bytes Total**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>System: Network Bytes Total</td>
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

- **Logical Disks Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>System: Logical Device {#LOGICALDEVICE} Read op/sec</td>
        <td>System: Logical Device {#LOGICALDEVICE} Write op/sec</td>
        <td>System: Logical Device {#LOGICALDEVICE} Queue</td>
        <td>System: Logical Device {#LOGICALDEVICE} Idle Time (%)</td>
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
        <td>System: Logical Devices Overview {#LOGICALDEVICE}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>System: Logical Device {#LOGICALDEVICE} Read op/sec <br> System: Logical Device {#LOGICALDEVICE} Write op/sec <br> System: Logical Device {#LOGICALDEVICE} Queue</td>
      </tr>
    </table>

## PostgreSQL metrics

### Archiving

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_count_files = 2

### Items

*Archiving metrics* use information from `pg_stat_archiver`.

- **Archived Files**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Archiver: Archived Files Count</td>
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


- **Attempts To Archive Files**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Archiver: Attempts to Archive Files Count</td>
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


- **Files Need To Archive**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Archiver: Files in archive_status Need to Archive Count</td>
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


- **Size Of Files Need To Archive**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Archiver: Files Need to Archive Size</td>
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
    <td>PostgreSQL Archiver: Archive Status</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Archiver: Files in archive_status Need to Archive Count <br> PostgreSQL Archiver: Archived Files Count <br> PostgreSQL Archiver: Attempts to Archive Files Count</td>
  </tr>
</table>

### Triggers

- **PostgreSQL Archiver: count files need to archive on {HOSTNAME} more than 2**  
    Triggers if *PostgreSQL Archiver: Files in archive_status Need to Archive Count* exceeds `max_count_files`.

## Autovacuum

### Items

*Autovacuum metrics* use information from `pg_stat_activity`.

- **Autovacuum Workers**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Autovacuum: Count of Autovacuum Workers</td>
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

- **Autovacuum Utilization (instant)**  

    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Autovacuum: Utilization per [MAMONSU_INTERVAL] seconds</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.autovacumm.utilization[]</td>
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

- **Autovacuum Utilization (average per 5 minutes)**  

    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Autovacuum: Utilization per 5 minutes</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.autovacumm.utilization.avg5[]</td>
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

- **Autovacuum Utilization (average per 15 minutes)**  

    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Autovacuum: Utilization per 15 minutes</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.autovacumm.utilization.avg15[]</td>
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

- **Autovacuum Utilization (average per 30 minutes)**  

    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Autovacuum: Utilization per 30 minutes</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.autovacumm.utilization.avg30[]</td>
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

    *Autovacuum Workers* evaluates as count of `pg_stat_activity.backend_type = 'autovacuum worker'` for PG 10+ and as summa of avtovacuum queries with not idle state for PG 9.6 and lower.

## Background Writer

### Items

*Background Writer metrics* use information from `pg_stat_bgwriter`.  

- **Buffers Allocated**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: Buffers Allocated</td>
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


- **Buffers Written**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: Buffers Written</td>
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


- **Buffers Written Directly By a Backend**  

    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: Buffers Written Directly by a Backend</td>
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


- **Buffers Written During Checkpoints**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: Buffers Written During Checkpoints</td>
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


- **Bgwriter Stopped a Cleaning Scan**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: Number of bgwriter Stopped by Max Write Count</td>
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


- **Backend Executes Its Own Fsync Call**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL bgwriter: Times a Backend Execute Its Own Fsync</td>
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
    <td>PostgreSQL bgwriter: Buffers</td>
    <td>PostgreSQL bgwriter: Events</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL bgwriter: Buffers Written During Checkpoints <br> PostgreSQL bgwriter: Buffers Written <br> PostgreSQL bgwriter: Buffers Written Directly by a Backend <br> PostgreSQL bgwriter: Buffers Allocated</td>
    <td>PostgreSQL bgwriter: Number of bgwriter Stopped by Max Write Count <br> PostgreSQL bgwriter: Times a Backend Execute Its Own Fsync</td>
  </tr>
</table>

### Blocks

### Items

*Blocks metrics* use information from `pg_stat_database`.

- **Blocks Hit**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Blocks Hit</td>
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


- **Blocks Read**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Blocks Read</td>
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
    <td>PostgreSQL Instance: Blocks Rate</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Instance: Blocks Hit <br> PostgreSQL Instance: Blocks Read</td>
  </tr>
</table>

### Checkpoints

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_checkpoint_by_wal_in_hour = 12

### Items

*Checkpoints metrics* use information from `pg_stat_bgwriter`.

- **Checkpoints Sync Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Checkpoints: Sync Time</td>
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


- **Checkpoints Write Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Checkpoints: Write Time</td>
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


- **Scheduled Checkpoints**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Checkpoints: by Timeout (in hour)</td>
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


- **Requested Checkpoints**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Checkpoints: by WAL (in hour)</td>
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
    <td>PostgreSQL Checkpoints: Count (in hour)</td>
    <td>PostgreSQL Checkpoints: Write/Sync</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Checkpoints: by Timeout (in hour) <br> PostgreSQL Checkpoints: by WAL (in hour)</td>
    <td>PostgreSQL Checkpoints: Write Time <br> PostgreSQL Checkpoints: Sync Time</td>
  </tr>
</table>

### Triggers

- **PostgreSQL Checkpoints: required checkpoints occurs too frequently on {HOSTNAME}**  
    Triggers if *PostgreSQL Checkpoints: by WAL (in hour)* exceeds `max_checkpoint_by_wal_in_hour`.

### Connections

Default config:  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;percent_connections_tr = 90

### Items

*Connections metrics* use information from `pg_stat_activity`.

- **Max Connections**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Max Connections</td>
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

    *Max Connections* maps `pg_settings.max_connections`.


- **Active**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Active User Connections</td>
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


- **Disabled**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Disabled User Connections</td>
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


- **Fastpath Function Call**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Fastpath Function Call User Connections</td>
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


- **Idle**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Idle User Connections</td>
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


- **Idle in Transaction**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Idle in Transaction User Connections</td>
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


- **Idle in Transaction (aborted)**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Idle in Transaction (Aborted) User Connections</td>
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


- **Total**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Total User Connections</td>
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

    *Total* calculates as summa of all connections from `pg_stat_activity` with `backend_type` represents user connections (*client backend, parallel worker*).


- **Waiting**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Waiting User Connections</td>
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

- **Other**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Connections: Number of Other Connections</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.connections[other]</td>
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
        <td>10+</td>
      </tr>
    </table>

    *Waiting* calculates as summa of all connections from `pg_stat_activity` with additional `backend_type`.

### Graphs

<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL Connections: Overview</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Connections: Number of Active User Connections <br> PostgreSQL Connections: Number of Idle User Connections <br> PostgreSQL Connections: Number of Idle In Transaction User Connections <br> PostgreSQL Connections: Number of Idle In Transaction (Aborted) User Connections <br> PostgreSQL Connections: Number of Fastpath Function Call User Connections <br> PostgreSQL Connections: Number of Disabled User Connections <br> PostgreSQL Connections: Number of Total User Connections <br> PostgreSQL Connections: Number of Waiting User Connections <br> PostgreSQL Connections: Max Connections</td>
  </tr>
</table>

### Triggers

- **PostgreSQL Connections: too many connections on {HOSTNAME} (total connections more than 90% of max_connections)**  
    Triggers if connections count exceeds `percent_connections_tr`.

### Databases

### Discovery Rules

- **PostgreSQL Databases Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Databases: Count of Bloating Tables in {#DATABASE}</td>
        <td>PostgreSQL Databases {#DATABASE}: size</td>
        <td>PostgreSQL Databases: Max datfrozenxid Age in: {#DATABASE}</td>
        <td>PostgreSQL Databases: Count of Invalid Indexes in {#DATABASE}</td>
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
        <td>PostgreSQL Databases: {#DATABASE} size</td>
        <td>PostgreSQL Databases: {#DATABASE} Bloating Overview</td>
        <td>PostgreSQL Databases: {#DATABASE} Max age(datfrozenxid)</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>PostgreSQL Databases {#DATABASE}: size</td>
        <td>PostgreSQL Databases: Count of Bloating Tables in {#DATABASE} <br> PostgreSQL Autovacuum: Count of Autovacuum Workers</td>
        <td>PostgreSQL Databases: Max datfrozenxid Age in: {#DATABASE} <br> PostgreSQL Autovacuum: Count of Autovacuum Workers</td>
      </tr>
    </table>

#### Triggers

- **PostgreSQL Databases: invalid indexes in {#DATABASE} (hostname={HOSTNAME} value={ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL: PostgreSQL Databases: Count of Invalid Indexes in {#DATABASE}* > 0.

### Events

### Items

*Events metrics* use information from `pg_stat_database`.

- **Conflicts**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Conflict Events</td>
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


- **Deadlocks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Deadlock Events</td>
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


- **Checksum Failures**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: checksum_failures Events</td>
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
    <td>PostgreSQL Instance: Events</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Instance: Conflict Events	<br> PostgreSQL Instance: Deadlock Events <br> PostgreSQL Instance: checksum_failures Events</td>
  </tr>
</table>

### Health

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;uptime = 600  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cache = 80

### Items


- **Server Version**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Health: Server Version</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.version[]</td>
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

    *Server Version* shows PostgreSQL/PostgresPro server version number.


- **Ping**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Health: Ping</td>
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


- **Cache Hit Ratio**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Health: Cache Hit Ratio</td>
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


- **Service Uptime**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Health: Service Uptime</td>
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

- **PostgreSQL Health: cache hit ratio too low on {HOSTNAME} ({ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL Health: Cache Hit Ratio* fails `cache`.

- **PostgreSQL Health: service has been restarted on {HOSTNAME} (uptime={ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL Health: Service Uptime* fails `uptime`.

- **PostgreSQL Health: no ping from PostgreSQL for 3 minutes on {HOSTNAME}**  
    Triggers if there is no data from *PostgreSQL Health: Ping* more than 3 minutes.

### Memory Leak

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;private_anon_mem_threshold = 1 Gb  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval = 60

### Items

- **private_anon_mem_threshold Exceeding Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Memory Leak: Number of Pids Which Private Anonymous Memory Exceeds private_anon_mem_threshold</td>
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

- **private_anon_mem_threshold Exceeding Messages Text**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Memory Leak: Number of Pids Which Private Anonymous Memory Exceeds private_anon_mem_threshold, text of message</td>
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
- **PostgreSQL Memory Leak: Number of Pids Which Private Anonymous Memory Exceeds private_anon_mem_threshold on {HOSTNAME}. {ITEM.LASTVALUE}**  
    Triggers if there is memory leak errors. Shows memory leak error messages text. 

### pg_buffercache

### Items

*pg_buffercache metrics* use information from `pg_buffercache`.

- **Shared Buffer Size**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL pg_buffercache: Shared Buffer Size</td>
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


- **Shared Buffer Twice Used Size**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL pg_buffercache: Shared Buffer Twice Used Size</td>
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


- **Shared Buffer Dirty Size**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL pg_buffercache: Shared Buffer Dirty Size</td>
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
    <td>PostgreSQL pg_buffercache: Shared Buffer</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL pg_buffercache: Shared Buffer Size <br> PostgreSQL pg_buffercache: Shared Buffer Twice Used Size <br> PostgreSQL pg_buffercache: Shared Buffer Dirty Size</td>
  </tr>
</table>

### pg_locks

### Items

*pg_locks metrics* use information from `pg_locks`.

- **Access Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX, CLUSTER, VACUUM FULL, LOCK TABLE</td>
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


- **Access Share**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: Read Only Queries</td>
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


- **Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: Locks From Application or Some Operations on System Catalogs</td>
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


- **Row Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: Write Queries</td>
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


- **Row Share**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: SELECT FOR SHARE and SELECT FOR UPDATE</td>
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


- **Share Row Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: Locks From Application</td>
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


- **Share Update Exclusive**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY</td>
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


- **Share**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Locks: CREATE INDEX</td>
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
    <td>PostgreSQL: Locks Sampling</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Locks: Read Only Queries <br> PostgreSQL Locks: SELECT FOR SHARE and SELECT FOR UPDATE <br> PostgreSQL Locks: Write Queries <br> PostgreSQL Locks: VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY <br> PostgreSQL Locks: CREATE INDEX <br> PostgreSQL Locks: Locks From Application <br> PostgreSQL Locks: Locks From Application or Some Operations on System Catalogs <br> PostgreSQL Locks: ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX, CLUSTER, VACUUM FULL, LOCK TABLE</td>
  </tr>
</table>

### Prepared Transactions

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_prepared_transaction_time = 18000

### Items

*Prepared Transactions metrics* use information from `pg_prepared_xacts`.   

- **Prepared Transactions Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Prepared Transactions: Number of Prepared Transactions</td>
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


- **Oldest Prepared Transaction Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Prepared Transactions: the Oldest Prepared Transaction Running Time in sec</td>
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
    <td>PostgreSQL Prepared Transactions: Overview</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Prepared Transactions: Number of Prepared Transactions	<br> PostgreSQL Prepared Transactions: the Oldest Prepared Transaction Running Time in sec</td>
  </tr>
</table>

### Triggers

- **PostgreSQL Prepared Transactions: prepared transaction is too old on {HOSTNAME}**  
    Triggers if *PostgreSQL Prepared Transactions: the Oldest Prepared Transaction Running Time in sec* exceeds `max_prepared_transaction_time`.

### Relations

### Discovery Rules

- **PostgreSQL Relations Sizes Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Relation Size: {#RELATIONNAME}</td>
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
        <td>PostgreSQL Relation Size: {#RELATIONNAME}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>PostgreSQL Relation Size: {#RELATIONNAME}</td>
      </tr>
    </table>

### Replication

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lag_more_than_in_sec = 300

### Items

*Replication metrics* use information from `pg_replication_slots`.


- **Server Mode**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Server Mode</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.server_mode</td>
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
   
    *Server Mode* shows server status as `MASTER` or `STANDBY`.


- **Non-active Replication Slots**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Replication: Count Non-Active Replication Slots</td>
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


- **Streaming Replication Lag**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Replication: Streaming Replication Lag</td>
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

- **PostgreSQL Replication Lag Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Delta of Total Lag</td>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Send Lag - Time elapsed sending recent WAL locally</td>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Receive Lag - Time elapsed between receiving recent WAL locally and receiving notification that this standby server has flushed it</td>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Write Lag - Time elapsed between flushing recent WAL locally and receiving notification that this standby server has written it</td>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Flush Lag - Time elapsed between flushing recent WAL locally and receiving notification that this standby server has written and flushed it</td>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Replay Lag - Time elapsed between flushing recent WAL locally and receiving notification that this standby server has written, flushed and applied</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.replication.total_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.send_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.receive_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.write_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.flush_lag[{#APPLICATION_NAME}]</td>
        <td>pgsql.replication.replay_lag[{#APPLICATION_NAME}]</td>
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
        <td>Bytes</td>
        <td>Bytes</td>
        <td>Bytes</td>
        <td>Bytes</td>
        <td>Bytes</td>
      </tr>
      <tr>
        <th>Delta</th>
        <td>As Is</td>
        <td>As Is</td>
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
        <td>PostgreSQL Replication: Delta of Total Lag for {#APPLICATION_NAME}</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>PostgreSQL Replication: {#APPLICATION_NAME} Delta of Total Lag</td>
      </tr>
    </table>

### Triggers

- **PostgreSQL Instance: server mode has been changed on {HOSTNAME} to {ITEM.LASTVALUE}**

- **PostgreSQL number of non-active replication slots on {HOSTNAME} (value={ITEM.LASTVALUE})**  

- **PostgreSQL streaming lag too high on {HOSTNAME} (value={ITEM.LASTVALUE})**  
    Triggers if *PostgreSQL Replication: Streaming Replication Lag* exceeds `lag_more_than_in_sec`.

### Statements

### Items

*Statements metrics* use information from `pg_stat_statements` and `pg_stat_statements_info` for PostgreSQL cluster and from `pgpro_stats` extension for PostgresPro cluster.

- **Amount of WAL Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Amount of WAL Files</td>
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


- **Amount of WAL Records**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Amount of WAL Records</td>
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


- **Dirty Bytes**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Dirty bytes/s</td>
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


- **WAL FPI**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Full Page Writes</td>
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


- **Read IO Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Read IO Time</td>
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


- **Write IO Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Write IO Time</td>
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


- **Other Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Other (mostly CPU) Time</td>
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


- **Read Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Read bytes/s</td>
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


- **Write Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Write bytes/s</td>
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


- **Last Statistic Reset**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Last Statistics Reset Time</td>
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


- **pg_stat_statements.max Exceeding Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Statements: Nnumber of Times pg_stat_statements.max Was Exceeded</td>
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
    <td>PostgreSQL Statements: Bytes</td>
    <td>PostgreSQL Statements: Spent Time</td>
    <td>PostgreSQL Statements: WAL Statistics</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Statements: Read bytes/s	<br> PostgreSQL Statements: Write bytes/s <br> PostgreSQL Statements: Dirty bytes/s</td>
    <td>PostgreSQL Statements: Read IO Time <br> PostgreSQL Statements: Write IO Time <br> PostgreSQL Statements: Other (mostly CPU) Time</td>
    <td>PostgreSQL Statements: Amount of WAL Files <br> PostgreSQL Statements: Amount of WAL Records <br> PostgreSQL Statements: Full Page Writes</td>
  </tr>
</table>

### Temp Files

### Items

*Temp Files metrics* use information from `pg_stat_database`.  

- **Temp Bytes**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Temp Bytes Written</td>
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


- **Temp Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Temp Files Created</td>
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
    <td>PostgreSQL Instance: Temp Files</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Instance: Temp Bytes Written <br> PostgreSQL Instance: Temp Files Created</td>
  </tr>
</table>

### Transactions

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_xid_age = 18000000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;max_transaction_time = 18000

### Items

- **Committed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Transactions Committed</td>
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


- **Rollbacks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Rollback Events</td>
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


- **Oldest Transaction Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Transactions: the Oldest Transaction Running Time in sec</td>
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


- **Oldest XID Age**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Transactions: Age of the Oldest XID</td>
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

- **PostgreSQL Transactions: the oldest XID is too big on {HOSTNAME}**  
    Triggers if *PostgreSQL Transactions: Age of the Oldest XID* exceeds `max_xid_age`.

- **PostgreSQL Transactions: running transaction is too old on {HOSTNAME}**  
    Triggers if *PostgreSQL Transactions: the Oldest Transaction Running Time in sec* exceeds `max_transaction_time`.

### Graphs
<table>
  <tr>
    <th>Name</th>
    <td>PostgreSQL Instance: Transactions Rate</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Instance: Transactions Committed	<br> PostgreSQL Instance: Rollback Events</td>
  </tr>
</table>

### Tuples

### Items

*Tuples metrics* use information from `pg_stat_database`.

- **Deleted**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Tuples Deleted</td>
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


- **Fetched**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Tuples Fetched</td>
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


- **Inserted**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Tuples Inserted</td>
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


- **Returned**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Tuples Returned</td>
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


- **Updated**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Instance: Tuples Updated</td>
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
    <td>PostgreSQL Instance: Tuples</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Instance: Tuples Deleted <br> PostgreSQL Instance: Tuples Fetched <br> PostgreSQL Instance: Tuples Inserted	avg <br> PostgreSQL Instance: Tuples Returned <br> PostgreSQL Instance: Tuples Updated</td>
  </tr>
</table>

### WAL

### Items

*WAL metrics* use information from `pg_stat_wal`.  

- **WAL Count**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Count of WAL Files</td>
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


- **WAL Write Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Write Speed</td>
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


- **WAL Buffers Full**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Buffers Full</td>
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


- **WAL FPI Generated**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Full Page Images Generated</td>
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


- **WAL Records Generated**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Records Generated</td>
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

- **WAL Sync Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Sync Time (ms)</td>
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


- **WAL Write Time**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Write Time (ms)</td>
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


- **WAL Sync Duty**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL WAL: Sync Duty (%)</td>
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
   
    *WAL Sync Duty* calculates as change of `wal_sync_time` per mamonsu interval.

## Postgres Pro metrics

### Compressed File System

Default config:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;force_enable = False

### Items

*Compressed File System metrics* use information from `cfs*` functions.

- **Compressed Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Compressed Files</td>
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


- **Scanned Files**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Scanned Files</td>
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


- **Current Ratio**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Current Ratio</td>
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

- **Total Ratio**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Total Ratio</td>
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

- **Scanned Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Scanned byte/s</td>
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


- **Written Speed**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Written byte/s</td>
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

- **PostgreSQL CFS Discovery**

    Items:
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL CFS: Relation {#COMPRESSED_RELATION} Compress Ratio</td>
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
        <td>PostgreSQL CFS: Relation {#COMPRESSED_RELATION} Compress Ratio</td>
      </tr>
      <tr>
        <th>Metrics</th>
        <td>PostgreSQL CFS: Relation {#COMPRESSED_RELATION} Compress Ratio</td>
      </tr>
    </table>

### Wait Sampling

### Items

*Wait Sampling metrics* use information from `pgpro_stats` extension by default or from `pg_wait_sampling` extension if you installed it on non-PostgrePro edition.  

***Locks in general***
- **Lightweight Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling: Lightweight Locks</td>
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

- **Heavyweight Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling: Heavyweight Locks</td>
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

- **Buffer Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling: Buffer Locks</td>
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

- **Client Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling: Client Locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.all_lock[client]</td>
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
        <td>10+</td>
      </tr>
    </table>

- **Extension Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling: Extension Locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.all_lock[extension]</td>
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
        <td>10+</td>
      </tr>
    </table>

- **Other Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling: Other Locks (e.g. IPC, Timeout, IO)</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.all_lock[other]</td>
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
- **Advisory User Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Advisory User Locks</td>
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

- **Extend a Relation Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Extend a Relation Locks</td>
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

- **Locks on a Page**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Locks on a Page</td>
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

- **Locks on a Relation**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Locks on a Relation</td>
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

- **Locks on a Tuple**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Locks on a Tuple</td>
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

- **Locks on Database Object**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Locks on Database Object</td>
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

- **Speculative Insertion Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Speculative Insertion Locks</td>
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

- **Transaction to Finish Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Transaction to Finish Locks</td>
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

- **Userlocks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Userlocks</td>
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

- **Virtual XID Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling HWLocks: Virtual XID Locks</td>
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
- **Autovacuum Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>	PostgreSQL Wait Sampling LWLocks: Autovacuum Locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[autovacuum]</td>
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

- **Buffer Operations Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: Buffer Operations Locks</td>
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

- **CLOG Access Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: CLOG Access Locks</td>
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

- **Logical Replication Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: Logical Replication Locks</td>
      </tr>
      <tr>
        <th>Key</th>
        <td>pgsql.lwlock[logical_replication]</td>
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
        <td>10+</td>
      </tr>
    </table>

- **Replication Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: Replication Locks</td>
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

- **WAL Access Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: WAL Access Locks</td>
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

- **XID Access Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: XID Access Locks</td>
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

- **Other Operations Lightweight Locks**  
   
    Zabbix item:  
    <table>
      <tr>
        <th>Name</th>
        <td>PostgreSQL Wait Sampling LWLocks: Other Operations Lightweight Locks</td>
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
    <td>PostgreSQL Wait Sampling: Heavyweight Locks</td>
    <td>PostgreSQL Wait Sampling: Lightweight Locks</td>
    <td>PostgreSQL Wait Sampling: Locks by Type</td>
  </tr>
  <tr>
    <th>Metrics</th>
    <td>PostgreSQL Wait Sampling HWLocks: Advisory User Locks <br> PostgreSQL Wait Sampling HWLocks: Extend a Relation Locks <br> PostgreSQL Wait Sampling HWLocks: Locks on a Page <br> PostgreSQL Wait Sampling HWLocks: Locks on a Relation <br> PostgreSQL Wait Sampling HWLocks: Locks on a Tuple <br> PostgreSQL Wait Sampling HWLocks: Locks on Database Object <br> PostgreSQL Wait Sampling HWLocks: Speculative Insertion Locks <br> PostgreSQL Wait Sampling HWLocks: Transaction to Finish Locks <br> PostgreSQL Wait Sampling HWLocks: Virtual XID Locks <br> PostgreSQL Wait Sampling HWLocks: Userlocks</td>
    <td>PostgreSQL Wait Sampling LWLocks: Autovacuum Locks <br> PostgreSQL Wait Sampling LWLocks: Buffer Operations Locks <br> PostgreSQL Wait Sampling LWLocks: Buffer Operations Locks <br> PostgreSQL Wait Sampling LWLocks: Logical Replication Locks <br> PostgreSQL Wait Sampling LWLocks: Logical Replication Locks <br> PostgreSQL Wait Sampling LWLocks: WAL Access Locks <br> PostgreSQL Wait Sampling LWLocks: WAL Access Locks <br> PostgreSQL Wait Sampling LWLocks: Other Operations Lightweight Locks</td>
    <td>PostgreSQL Wait Sampling: Lightweight Locks <br> PostgreSQL Wait Sampling: Heavyweight Locks <br> PostgreSQL Wait Sampling: Buffer Locks <br> PostgreSQL Wait Sampling: Client Locks <br> PostgreSQL Wait Sampling: Extension Locks <br> PostgreSQL Wait Sampling: Other Locks (e.g. IPC, Timeout, IO)</td>
  </tr>
</table>
