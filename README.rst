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
    $ cp dist\{mamonsu, service_win32}.exe c:\mamonsu
    $ c:\mamonsu\mamonsu.exe -w c:\mamonsu\agent.conf
    $ c:\mamonsu\service_win32.exe -install
    $ net start mamonsu


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

    [plugins]
    directory = /etc/mamonsu/plugins

    [log]
    file = /var/log/mamonsu/agent.log
    level = INFO

==================
Write your plugin
==================

All plugins must exist in plugin directory which is defined in your configuration file.

See the `example <https://github.com/postgrespro/mamonsu/blob/master/conf/plugin.py>`_ for aditional information.

After add new plugin, you must to reexport template and import this file to zabbix.

====
Run
====

.. code-block:: bash

    $ service mamonsu status
    or by hand:
    $ mamonsu -c /etc/mamonsu/agent.conf -p /var/run/mamonsu.pid
