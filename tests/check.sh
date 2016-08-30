#!/bin/sh -ex

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
yum install -y https://download.postgresql.org/pub/repos/yum/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-2.noarch.rpm
yum install -y postgresql95-server
su postgres -c '/usr/pgsql-9.5/bin/initdb -D /var/lib/pgsql/9.5/data'
/etc/init.d/postgresql-9.5 start

# mamonsu report
(mamonsu report | grep version | grep 'PostgreSQL 9.5') || exit 1

# mamonsu tune
mamonsu tune

# export config
mamonsu -w /dev/null

# write zabbix template
mamonsu -e $ZABBIX_TEMPLATE -t $ZABBIX_TEMPLATE_NAME
grep 'pgsql\.uptime\[\]' /tmp/template.xml || exit 2
grep 'system\.disk\.all_read' /tmp/template.xml || exit 2

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
\$DB["SERVER"]    = 'localhost';
\$DB["PORT"]      = '5432';
\$DB["DATABASE"]  = 'zabbix';
\$DB["USER"]      = 'zabbix';
\$DB["SCHEMA"]    = '';
\$ZBX_SERVER      = 'localhost';
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

# start mamonsu and sleep
cat <<EOF > /etc/mamonsu/agent.conf
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
/etc/init.d/mamonsu start
sleep 125

# check metric from agent
mamonsu agent -c /etc/mamonsu/agent.conf version
mamonsu agent metric-get system.disk.all_read[] -c /etc/mamonsu/agent.conf
mamonsu agent -c /etc/mamonsu/agent.conf metric-list | grep system

# metric log
grep utilization /tmp/localhost.log || exit 3
grep 'pgsql\.uptime' /tmp/localhost.log || exit 3

# error in zabbix server
(mamonsu zabbix item error $ZABBIX_CLIENT_HOST | grep ZBX_NOTSUPPORTED) && exit 4

# other metric in zabbix server
(mamonsu zabbix item lastvalue $ZABBIX_CLIENT_HOST | grep uptime) || exit 5

# all plugin alive
grep -i 'Plugin exception' /var/log/mamonsu/agent.log && exit 6

exit 0
