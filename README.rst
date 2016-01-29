*******************************
mamonsu: Active zabbix agent
*******************************

============
Installation
============

Install via pip:

.. code-block:: bash

    $ pip install mamonsu

Install from git:

.. code-block:: bash

    $ git clone ... && cd mamonsu && python setup.py build && python setup.py install

Build deb:

.. code-block:: bash

    $ apt-get install debhelper python-dev python-setuptools
    $ git clone ... && make deb && dpkg -i mamonsu*.deb

Build rpm:

.. code-block:: bash

    $ yum install python2-devel python-setuptools
    $ git clone ... && make rpm && rpm -i mamonsu*.rpm

==========
Configure
==========

Export template for zabbix:

.. code-block:: bash

    $ mamonsu -e template.xml

Import this file in web interface of zabbix: Configuration => Templates => Import.

Add this template like `PostgrePro-Linux` at your monitoring host.

Generate config on monitring host:

.. code-block:: bash

    $ mamonsu -w /etc/mamonsu/agent.conf

Change previously zabbix server address and client hostname:

.. code-block:: bash

    $ vim /etc/mamonsu/agent.conf

    $ cat /etc/mamonsu/agent.conf

    [zabbix]
    client = zabbix_client_host_name
    address = zabbix_server_ip

    [postgres]
    user = postgres
    password = None
    database = postgres
    host = localhost
    port = 5432
    query_timeout = 10

    [log]
    file = /var/log/mamonsu/agent.log
    level = INFO

====
Run
====

.. code-block:: bash

    $ mamonsu -c /etc/mamonsu/agent.conf -p /var/run/mamonsu.pid
