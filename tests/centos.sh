#!/bin/sh -ex

# test build
cd /var/tmp
yum install -y tar make rpm-build python2-devel python-setuptools
make rpm && rpm -i mamonsu*.rpm
cd /

# test alive after 5 sec
/etc/init.d/mamonsu restart
sleep 5
/etc/init.d/mamonsu stop

# test report
yum install -y https://download.postgresql.org/pub/repos/yum/9.5/redhat/rhel-6-x86_64/pgdg-centos95-9.5-2.noarch.rpm
yum install -y postgresql95-server
su postgres -c '/usr/pgsql-9.5/bin/initdb -D /var/lib/pgsql/9.5/data'
/etc/init.d/postgresql-9.5 start
mamonsu report | grep version | grep 'PostgreSQL 9.5'

# test export
mamonsu -e /tmp/template.xml
grep 'pgsql\.uptime\[\]' /tmp/template.xml
grep 'system\.disk\.all_read' /tmp/template.xml
mamonsu -w /tmp/agent.conf

# test metric send
cat <<EOF > /etc/mamonsu/agent.conf
[zabbix]
enabled = False

[metric_log]
enabled = True
directory = /tmp

[log]
file = /var/log/mamonsu/agent.log
level = DEBUG
EOF
/etc/init.d/mamonsu restart && sleep 125
grep utilization /tmp/localhost.log
grep 'pgsql\.uptime' /tmp/localhost.log
# check failed plugin
grep -i 'Plugin exception' /var/log/mamonsu/agent.log && exit 1
# test uninstall
yum remove -y mamonsu
