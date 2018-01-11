#!/bin/bash -ex

export TESTDIR=$(dirname $0)
export ZABBIX_USER=Admin
export ZABBIX_PASSWD=zabbix
export ZABBIX_URL='http://localhost/zabbix'
export ZABBIX_CLIENT_HOST=zabbix_client_host
export ZABBIX_TEMPLATE=/tmp/template.xml
export ZABBIX_TEMPLATE_NAME='PostgresPro'

# install mamonsu
cp -a /var/tmp /root/mamonsu && pushd /root/mamonsu
yum install -y tar make rpm-build python2-devel python-setuptools
make rpm && yum install -y mamonsu*.rpm

# install postgres
yum install -y https://download.postgresql.org/pub/repos/yum/9.5/redhat/rhel-6-x86_64/pgdg-centos95-9.5-3.noarch.rpm
yum install -y postgresql95-server postgresql95-contrib
su postgres -c '/usr/pgsql-9.5/bin/initdb -D /var/lib/pgsql/9.5/data'
su postgres -c '/usr/pgsql-9.5/bin/pg_ctl start -w -D /var/lib/pgsql/9.5/data'

# mamonsu tune
echo "shared_preload_libraries = '\"\$libdir/pg_stat_statements\"'" > /var/lib/pgsql/9.5/data/postgresql.auto.conf
su postgres -c '/usr/pgsql-9.5/bin/pg_ctl restart -w -D /var/lib/pgsql/9.5/data'
mamonsu tune
su postgres -c '/usr/pgsql-9.5/bin/pg_ctl restart -w -D /var/lib/pgsql/9.5/data'
grep "shared_preload_libraries \= '\"\$libdir/pg_stat_statements\", pg_buffercache'" /var/lib/pgsql/9.5/data/postgresql.auto.conf || (cat /var/lib/pgsql/9.5/data/postgresql.auto.conf && exit 1)

# mamonsu report
(mamonsu report | grep version | grep 'PostgreSQL 9.5') || exit 2

# export config
cat <<EOF > /etc/mamonsu/plugins/def_conf_test.py
import os
from mamonsu.lib.plugin import Plugin

class DefConfTest(Plugin):

    DEFAULT_CONFIG = {
        'config': 'external_plugin_config',
    }

    def run(cls, zbx):
        cls.log.error(cls.plugin_config('config'))
        os.system("touch /tmp/extenal_plugin_is_called")
EOF
mamonsu export config /tmp/config
grep external_plugin_config /tmp/config || exit 3
sed -i 's|.*max_checkpoint_by_wal_in_hour =.*|max_checkpoint_by_wal_in_hour = 5555555555555|g' /tmp/config

# write zabbix template
mamonsu export template $ZABBIX_TEMPLATE -t $ZABBIX_TEMPLATE_NAME -c /tmp/config
grep 5555555555555 /tmp/template.xml || exit 4
grep 'pgsql\.uptime\[\]' /tmp/template.xml || exit 4
grep 'system\.disk\.all_read' /tmp/template.xml || exit 4

# test export config
cat <<EOF > /etc/mamonsu/agent.conf
[zabbix]
enabled = False

[agent]
enabled = False

[plugins]
enabled = False

[defconftest]
config = external_plugin_config2
EOF
mamonsu export config /tmp/config -a /etc/mamonsu/plugins -c /etc/mamonsu/agent.conf
grep external_plugin_config2 /tmp/config || exit 5

# install zabbix
yum install -y http://repo.zabbix.com/zabbix/2.4/rhel/6/x86_64/zabbix-release-2.4-1.el6.noarch.rpm
yum install -y zabbix-server-pgsql zabbix-web-pgsql
sed -i "s,;date.timezone =,date.timezone = 'US/Eastern'," /etc/php.ini
su postgres -c 'createdb zabbix'
su postgres -c 'createuser -a -d -E zabbix'
psql -1 -f $TESTDIR/zabbix_sql/schema.sql -U zabbix -d zabbix
psql -1 -f $TESTDIR/zabbix_sql/images.sql -U zabbix -d zabbix
psql -1 -f $TESTDIR/zabbix_sql/data.sql -U zabbix -d zabbix
cat <<EOF > /etc/zabbix/zabbix_server.conf
AlertScriptsPath=/usr/lib/zabbix/alertscripts
ExternalScripts=/usr/lib/zabbix/externalscripts
LogFile=/var/log/zabbix/zabbix_server.log
LogFileSize=0
PidFile=/var/run/zabbix/zabbix_server.pid
SNMPTrapperFile=/var/log/snmptt/snmptt.log

DBHost=127.0.0.1
DBName=zabbix
DBUser=zabbix
EOF
cat <<EOF > /usr/share/zabbix/conf/zabbix.conf.php
<?php
global \$DB;
\$DB["TYPE"]      = 'POSTGRESQL';
\$DB["SERVER"]    = '127.0.0.1';
\$DB["PORT"]      = '5432';
\$DB["DATABASE"]  = 'zabbix';
\$DB["USER"]      = 'zabbix';
\$DB["SCHEMA"]    = '';
\$ZBX_SERVER      = '127.0.0.1';
\$ZBX_SERVER_PORT = '10051';
\$ZBX_SERVER_NAME = '';
\$IMAGE_FORMAT_DEFAULT = IMAGE_FORMAT_PNG;
?>
EOF
cp /usr/share/zabbix/conf/zabbix.conf.php /etc/zabbix/web/zabbix.conf.php
/etc/init.d/zabbix-server start
/etc/init.d/httpd start

# export template to zabbix
mamonsu zabbix template export $ZABBIX_TEMPLATE
template_id=$(mamonsu zabbix template id $ZABBIX_TEMPLATE_NAME)
hostgroup_id=$(mamonsu zabbix hostgroup id 'Linux servers')
mamonsu zabbix host create $ZABBIX_CLIENT_HOST $hostgroup_id $template_id 127.0.0.1

su postgres -c 'createdb mamonsu'
su postgres -c "/usr/pgsql-9.5/bin/psql -Atc \"CREATE USER mamonsu WITH password 'supersecret'\""
cat <<EOF > /var/lib/pgsql/9.5/data/pg_hba.conf
local   all             all                                     trust
host    zabbix          zabbix          127.0.0.1/32            trust
host    zabbix          zabbix          ::1/128                 trust
host    all             all             127.0.0.1/32            md5
EOF
su postgres -c '/usr/pgsql-9.5/bin/pg_ctl reload -D /var/lib/pgsql/9.5/data'

# start mamonsu and sleep
cat <<EOF > /etc/mamonsu/agent.conf
[postgres]
host = 127.0.0.1
user = mamonsu
database = mamonsu
password = supersecret

[zabbix]
enabled = True
address = 127.0.0.1
client = $ZABBIX_CLIENT_HOST

[agent]
enabled = True
host = 127.0.0.1
port = 10053

[metric_log]
enabled = True
directory = /tmp

[log]
file = /var/log/mamonsu/agent.log
level = DEBUG
EOF
mamonsu bootstrap -U postgres mamonsu -M mamonsu
/etc/init.d/mamonsu start
sleep 125

# check external plugin is worked
file /tmp/extenal_plugin_is_called || exit 6

# check metric from agent
mamonsu agent -c /etc/mamonsu/agent.conf version
mamonsu agent metric-get system.disk.all_read[] -c /etc/mamonsu/agent.conf
mamonsu agent -c /etc/mamonsu/agent.conf metric-list | grep system

# metric log
grep utilization /tmp/localhost.log || exit 7
grep 'pgsql\.uptime' /tmp/localhost.log || exit 7

# error in zabbix server
(mamonsu zabbix item error $ZABBIX_CLIENT_HOST | grep ZBX_NOTSUPPORTED) && exit 8

# other metric in zabbix server
(mamonsu zabbix item lastvalue $ZABBIX_CLIENT_HOST | grep uptime) || exit 9

# all plugin alive, exclude pg_wait_sampling
(grep -v 'PGWAITSAMPLING' /var/log/mamonsu/agent.log | grep -i 'catch error') && exit 10

exit 0
