****************************************
mamonsu: Monitoring agent for PostgreSQL
****************************************

============
Build status
============
.. image:: https://travis-ci.org/postgrespro/mamonsu.svg?branch=master
    :target: https://travis-ci.org/postgrespro/mamonsu

========
License
========

Development version, available on github, released under BSD 3-clause.

============
Installation
============

Pre-Build packages for:

    Linux distros: https://packagecloud.io/postgrespro/mamonsu

    `Windows installers <https://oc.postgrespro.ru/index.php/s/qu7YsFvOE55LdXo>`_

Install via pip:

.. code-block:: bash

    $ pip install mamonsu

Install from git:

.. code-block:: bash

    $ git clone ... && cd mamonsu && python setup.py build && python setup.py install

Build deb:

.. code-block:: bash

    $ apt-get install make dpkg-dev debhelper python-dev python-setuptools
    $ git clone ... && cd mamonsu && make deb && dpkg -i mamonsu*.deb

Build rpm:

.. code-block:: bash

    $ yum install make rpm-build python2-devel python-setuptools
    $ git clone ... && cd mamonsu && make rpm && rpm -i mamonsu*.rpm

Build win32 exe: (worked with python v3.4: py2exe v0.9.2.2 and pywin32 v220 or python v2.7: py2exe v0.6.9 and pywin32 v220):
If you have error with ctypes and python v3.4: try to extend bootstrap_modules (add "ctypes") in Lib\site-packages\py2exe\runtime.py

.. code-block:: bash

    $ git clone ... && cd mamonsu && python setup_win32.py py2exe
    $ cp dist\{mamonsu, service_win32}.exe c:\mamonsu
    $ c:\mamonsu\mamonsu.exe -w c:\mamonsu\agent.conf
    $ c:\mamonsu\service_win32.exe -install
    $ net start mamonsu

Build nsis installer:

.. code-block:: bash

    $ git clone ... && cd mamonsu && python setup_win32.py py2exe
    $ nsis packaging/win/mamonsu.nsis

==========
Configure
==========

Export template for zabbix:

.. code-block:: bash

    $ mamonsu export template template.xml --add-plugins /etc/mamonsu/plugins
    or
    $ wget https://raw.githubusercontent.com/postgrespro/mamonsu/master/packaging/conf/template.xml
    or
    $ cp /usr/share/mamonsu/template.xml .

Import this file in web interface of zabbix: Configuration => Templates => Import, or deploy with mamonsu:

.. code-block:: bash

    $ mamonsu zabbix template export /usr/share/mamonsu/template.xml --url=http://zabbix/ --user=Admin --password=zabbix

Add this template like `PostgresPro-Linux` at your monitoring host, or create host with mamonsu:

.. code-block:: bash

    $ mamonsu zabbix host create <client name> <hostgroup id> <template id> <ip> --url=http://zabbix/ --user=Admin --password=zabbix

Generate config on monitring host (or use preinstalled):

.. code-block:: bash

    $ mamonsu export config /etc/mamonsu/agent.conf --add-plugins /etc/mamonsu/plugins

Change previously zabbix server address and client hostname:

.. code-block:: bash

    $ vim /etc/mamonsu/agent.conf

    $ cat /etc/mamonsu/agent.conf

    [zabbix]
    ; enabled by default
    enabled = True
    client = zabbix_client_host_name
    address = zabbix_server_ip

    [postgres]
    ; enabled by default
    enabled = True
    user = mamonsu
    database = mamonsu
    ; empty password
    password = None
    port = 5432
    query_timeout = 10

    [system]
    ; enabled by default
    enabled = True

    [log]
    file = /var/log/mamonsu/agent.log
    level = INFO

Deploy DDL for monitoring (if you want to monitoring without superuser rights)

.. code-block:: bash

    $ mamonsu deploy -U postgres -d mamonsu

==================
Write your plugin
==================

All plugins must exist in plugin directory which is defined in your configuration file.

See the `examples <https://github.com/postgrespro/mamonsu/tree/master/examples>`_ for aditional information.

After add new plugin, you must to reexport template and import this file to zabbix.

====
Run
====

.. code-block:: bash

    $ service mamonsu start
    or by hand:
    $ mamonsu -d -a /etc/mamonsu/plugins -c /etc/mamonsu/agent.conf -p /var/run/mamonsu.pid

====================
Metrics:  PostgreSQL
====================

.. code-block:: bash

    'PostgreSQL: ping': pgsql.ping[]
    'PostgreSQL: service uptime': pgsql.uptime[]
    'PostgreSQL: cache hit ratio': pgsql.cache[hit]
    'PostgreSQL: number of total connections': pgsql.connections[total]
    'PostgreSQL: number of waiting connections': pgsql.connections[waiting]
    'PostgreSQL: number of active connections': pgsql.connections[active]
    'PostgreSQL: number of idle connections': pgsql.connections[idle]
    'PostgreSQL: number of idle in transaction connections': pgsql.connections[idle_in_transaction]
    'PostgreSQL checkpoints: by timeout': pgsql.checkpoints[checkpoints_timed]
    'PostgreSQL checkpoints: required': pgsql.checkpoints[checkpoints_req]
    'PostgreSQL checkpoint: write time': pgsql.checkpoint[write_time]
    'PostgreSQL checkpoint: sync time': pgsql.checkpoint[checkpoint_sync_time]
    'PostgreSQL bgwriter: buffers written during checkpoints': pgsql.bgwriter[buffers_checkpoint]
    'PostgreSQL bgwriter: buffers written': pgsql.bgwriter[buffers_clean]
    'PostgreSQL bgwriter: number of bgwriter stopped by max write count': pgsql.bgwriter[maxwritten_clean]
    'PostgreSQL bgwriter: buffers written directly by a backend': pgsql.bgwriter[buffers_backend]
    'PostgreSQL bgwriter: times a backend execute its own fsync': pgsql.bgwriter[buffers_backend_fsync]
    'PostgreSQL bgwriter: buffers allocated': pgsql.bgwriter[buffers_alloc]
    'PostgreSQL: count of autovacuum workers': pgsql.autovacumm.count[]
    'PostgreSQL transactions: total': pgsql.transactions[total]
    'PostgreSQL blocks: hit': pgsql.blocks[hit]
    'PostgreSQL blocks: read': pgsql.blocks[read]
    'PostgreSQL event: conflicts': pgsql.events[conflicts]
    'PostgreSQL event: deadlocks': pgsql.events[deadlocks]
    'PostgreSQL event: rollbacks': pgsql.events[xact_rollback]
    'PostgreSQL temp: bytes written': pgsql.temp[bytes]
    'PostgreSQL temp: files created': pgsql.temp[files]
    'PostgreSQL tuples: deleted': pgsql.tuples[deleted]
    'PostgreSQL tuples: fetched': pgsql.tuples[fetched]
    'PostgreSQL tuples: inserted': pgsql.tuples[inserted]
    'PostgreSQL tuples: returned': pgsql.tuples[returned]
    'PostgreSQL tuples: updated': pgsql.tuples[updated]
    'PostgreSQL: streaming replication lag in seconds': pgsql.replication_lag[sec]
    'PostgreSQL: wal write speed': pgsql.wal.write[]
    'PostgreSQL: count of xlog files': pgsql.wal.count[]
    'PostgreSQL statements: read bytes/s': pgsql.stat[read_bytes]
    'PostgreSQL statements: write bytes/s': pgsql.stat[write_bytes]
    'PostgreSQL statements: dirty bytes/s': pgsql.stat[dirty_bytes]
    'PostgreSQL statements: read io time': pgsql.stat[read_time]
    'PostgreSQL statements: write io time': pgsql.stat[write_time]
    'PostgreSQL statements: other (mostly cpu) time': pgsql.stat[other_time]
    'PostgreSQL waits: Lightweight locks': pgsql.all_lock[lwlock]
    'PostgreSQL waits: Heavyweight locks': pgsql.all_lock[hwlock]
    'PostgreSQL waits: Buffer locks': pgsql.all_lock[buffer]
    'PostgreSQL waits: lock on a relation': pgsql.hwlock[relation]
    'PostgreSQL waits: extend a relation': pgsql.hwlock[extend]
    'PostgreSQL waits: lock on a tuple': pgsql.hwlock[tuple]
    'PostgreSQL waits: transaction to finish': pgsql.hwlock[transactionid]
    'PostgreSQL waits: virtual xid lock': pgsql.hwlock[virtualxid]
    'PostgreSQL waits: speculative insertion lock': pgsql.hwlock[speculative_token]
    'PostgreSQL waits: lock on database object': pgsql.hwlock[object]
    'PostgreSQL waits: userlock': pgsql.hwlock[userlock]
    'PostgreSQL waits: advisory user lock': pgsql.hwlock[advisory]
    'PostgreSQL waits: XID access': pgsql.lwlock[xid]
    'PostgreSQL waits: WAL access': pgsql.lwlock[wal]
    'PostgreSQL waits: CLOG access': pgsql.lwlock[clog]
    'PostgreSQL waits: Replication Locks': pgsql.lwlock[replication]
    'PostgreSQL waits: Buffer operations': pgsql.lwlock[buffer]
    'PostgreSQL waits: Other operations': pgsql.lwlock[other]

    'Database {#DATABASE}: size': pgsql.database.size[{#DATABASE}]
    'Count of bloating tables in database: {#DATABASE}': pgsql.database.bloating_tables[{#DATABASE}]
    'Max age (datfrozenxid) in: {#DATABASE}': pgsql.database.bloating_tables[{#DATABASE}]


=====================
Metrics: Linux system
=====================

.. code-block:: bash

    'System uptime': system.uptime[]
    'System load average over 1 minute': system.la[1]
    'Processes: in state running': system.processes[running]
    'Processes: in state blocked': system.processes[blocked]
    'Processes: forkrate': system.processes[forkrate]
    'Opened files': system.open_files[]
    'CPU time spent by normal programs and daemons': system.cpu[user]
    'CPU time spent by nice(1)d programs': system.cpu[nice]
    'CPU time spent by the kernel in system activities': system.cpu[system]
    'CPU time spent by Idle CPU time': system.cpu[idle]
    'CPU time spent waiting for I/O operations': system.cpu[iowait]
    'CPU time spent handling interrupts': system.cpu[irq]
    'CPU time spent handling batched interrupts': system.cpu[softirq]
    'Block devices: read requests': system.disk.all_read[]
    'Block devices: write requests': system.disk.all_write[]
    'Apps: User-space applications': system.memory[apps]
    'Buffers: Block device cache and dirty': system.memory[buffers]
    'Swap: Swap space used': system.memory[swap]
    'Cached: Parked file data (file content) cache': system.memory[cached]
    'Free: Wasted memory': system.memory[unused]
    'Slab: Kernel used memory (inode cache)': system.memory[slab]
    'SwapCached: Fetched unmod yet swap pages': system.memory[swap_cache]
    'PageTables: Map bt virtual and physical': system.memory[page_tables]
    'VMallocUsed: vmaloc() allocated by kernel': system.memory[vmalloc_used]
    'Committed_AS: Total committed memory': system.memory[committed]
    'Mapped: All mmap()ed pages': system.memory[mapped]
    'Active: Memory recently used': system.memory[active]
    'Inactive: Memory not currently used': system.memory[inactive]

    'Mount point {#MOUNTPOINT}: used': system.vfs.used[{#MOUNTPOINT}]
    'Mount point {#MOUNTPOINT}: free' system.vfs.free[{#MOUNTPOINT}]
    'Mount point {#MOUNTPOINT}: free in percents': system.vfs.percent_free[{#MOUNTPOINT}]
    'Mount point {#MOUNTPOINT}: free inodes in percent': system.vfs.percent_inode_free[{#MOUNTPOINT}]
    'Block device {#BLOCKDEVICE}: utilization': system.disk.utilization[{#BLOCKDEVICE}]
    'Block device {#BLOCKDEVICE}: read operations': system.disk.read[{#BLOCKDEVICE}]
    'Block device {#BLOCKDEVICE}: write operations': system.disk.write[{#BLOCKDEVICE}]
    'Net device {#NETDEVICE}: RX bytes/s': system.net.rx_bytes[{#NETDEVICE}]
    'Net device {#NETDEVICE}: RX errors/s': system.net.rx_errors[{#NETDEVICE}]
    'Net device {#NETDEVICE}: RX drops/s': system.net.rx_drops[{#NETDEVICE}]
    'Net device {#NETDEVICE}: TX bytes/s': system.net.tx_bytes[{#NETDEVICE}]
    'Net device {#NETDEVICE}: TX errors/s': system.net.tx_errors[{#NETDEVICE}]
    'Net device {#NETDEVICE}: TX drops/s': system.net.tx_drops[{#NETDEVICE}]

=======================
Metrics: Windows system
=======================

.. code-block:: bash

    'Memory cached': system.memory[cache]
    'Memory available': system.memory[available]
    'Memory free': system.memory[free]
    'CPU user time': system.cpu[user_time]
    'CPU idle time': system.cpu[idle_time]
    'CPU privileged time': system.cpu[privileged_time]
    'Network bytes total': system.network[total_bytes]
    'Network output queue length': system.network[total_output_queue]

============
Screenshots
============

.. image::  https://raw.githubusercontent.com/postgrespro/mamonsu/master/examples/statistics.png


============
Tool: Report
============

Create report about used hardware and PostgreSQL:

.. code-block:: bash

    $ mamonsu report

==========
Tool: Tune
==========

Make generic optimization for system and PostgreSQL, based on hardware information:

.. code-block:: bash

    $ mamonsu tune

==========================
Tool: analog of zabbix_get
==========================

.. code-block:: bash

    $ mamonsu agent version
    $ mamonsu agent metric-list
    $ mamonsu agent metric-get <key>

================
Tool: Zabbix CLI
================

Simple cli for control your Zabbix Server

.. code-block:: bash

    $ export ZABBIX_USER=Admin
    $ export ZABBIX_PASSWD=zabbix
    $ export ZABBIX_URL='http://localhost/zabbix'

    $ mamonsu zabbix template list
    $ mamonsu zabbix template show <template name>
    $ mamonsu zabbix template id <template name>
    $ mamonsu zabbix template delete <template id>
    $ mamonsu zabbix template export <file>

    $ mamonsu zabbix host list
    $ mamonsu zabbix host show <hostname>
    $ mamonsu zabbix host id <hostname>
    $ mamonsu zabbix host delete <host id>
    $ mamonsu zabbix host create <host name> <hostgroup id> <template id> <ip>
    $ mamonsu zabbix host info templates <host id>
    $ mamonsu zabbix host info hostgroups <host id>
    $ mamonsu zabbix host info graphs <host id>
    $ mamonsu zabbix host info items <host id>

    $ mamonsu zabbix hostgroup list
    $ mamonsu zabbix hostgroup show <hostgroup name>
    $ mamonsu zabbix hostgroup id <hostgroup name>
    $ mamonsu zabbix hostgroup delete <hostgroup id>
    $ mamonsu zabbix hostgroup create <hostgroup name>

    $ mamonsu zabbix item error <host name>
    $ mamonsu zabbix item lastvalue <host name>
    $ mamonsu zabbix item lastclock <host name>
