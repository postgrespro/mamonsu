*******************************
mamonsu: Active zabbix agent
*******************************

============
Build status
============
.. image:: https://travis-ci.org/postgrespro/mamonsu.svg?branch=master
    :target: https://travis-ci.org/postgrespro/mamonsu

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


==========
Configure
==========

Export template for zabbix:

.. code-block:: bash

    $ mamonsu -e template.xml

Import this file in web interface of zabbix: Configuration => Templates => Import.

Add this template like `PostgresPro-Linux` at your monitoring host.

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

    $ service mamonsu status
    or by hand:
    $ mamonsu -c /etc/mamonsu/agent.conf -p /var/run/mamonsu.pid
