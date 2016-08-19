*******************************
mamonsu: Active zabbix agent
*******************************

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

    `Windows installers <https://oc.postgrespro.ru/index.php/s/qkGzj8MPLIqNhQv>`_

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

Build exe (worked with python v3.4, py2exe v0.9.2.2, pywin32 v220):

If you have error with ctypes: try to extend bootstrap_modules (add "ctypes") in Lib\site-packages\py2exe\runtime.py

.. code-block:: bash

    $ git clone ... && cd mamonsu && python setup_win32.py py2exe
    $ cp dist\{mamonsu, service_win32}.exe c:\mamonsu
    $ c:\mamonsu\mamonsu.exe -w c:\mamonsu\agent.conf
    $ c:\mamonsu\service_win32.exe -install
    $ net start mamonsu

Build nsis installer(Don`t forget to sign it afterwards):

.. code-block:: bash

    $ git clone ... && cd mamonsu && python setup_win32.py py2exe
    $ nsis win/mamonsu.nsis

==========
Configure
==========

Export template for zabbix:

.. code-block:: bash

    $ mamonsu -e template.xml
    or
    $ wget https://raw.githubusercontent.com/postgrespro/mamonsu/master/conf/template.xml
    or
    $ cp /usr/share/mamonsu/template.xml .

Import this file in web interface of zabbix: Configuration => Templates => Import.

Add this template like `PostgresPro-Linux` at your monitoring host.

Generate config on monitring host (or use preinstalled):

.. code-block:: bash

    $ mamonsu -w /etc/mamonsu/agent.conf

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
    user = postgres
    database = postgres
    ; empty password
    password = None
    port = 5432
    query_timeout = 10

    [system]
    ; enabled by default
    enabled = True

    [plugins]
    ; directory with user plugins
    directory = /etc/mamonsu/plugins

    [log]
    file = /var/log/mamonsu/agent.log
    level = INFO

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

    $ service mamonsu status
    or by hand:
    $ mamonsu -c /etc/mamonsu/agent.conf -p /var/run/mamonsu.pid

===============
Report tool
===============

.. code-block:: bash

    $ mamonsu report --help

====================
Auto tune PostgreSQL
====================

.. code-block:: bash

    $ mamonsu tune --help

===============
Screenshots
===============

.. image::  https://raw.githubusercontent.com/postgrespro/mamonsu/master/examples/statistics.png

==================
PostgreSQL metrics
==================

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

    'Database {#DATABASE}: size': pgsql.database.size[{#DATABASE}]
    'Count of bloating tables in database: {#DATABASE}': pgsql.database.bloating_tables[{#DATABASE}]
    'Max age (datfrozenxid) in: {#DATABASE}': pgsql.database.bloating_tables[{#DATABASE}]


====================
Linux system metrics
====================

.. code-block:: bash

    'Processes: in state running': system.processes[running]
    'Processes: in state blocked': system.processes[blocked]
    'Processes: forkrate': system.processes[forkrate]
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

======================
Windows system metrics
======================

.. code-block:: bash

    'Memory cached': system.memory[cache]
    'Memory available': system.memory[available]
    'Memory free': system.memory[free]
    'CPU user time': system.cpu[user_time]
    'CPU idle time': system.cpu[idle_time]
    'CPU privileged time': system.cpu[privileged_time]
    'Network bytes total': system.network[total_bytes]
    'Network output queue length': system.network[total_output_queue]
