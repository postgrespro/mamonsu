#!/bin/sh -ex

# install mamonsu
cp -a /var/tmp /root/mamonsu && pushd /root/mamonsu
yum install -y tar make rpm-build python2-devel python-setuptools
make rpm && rpm -i mamonsu*.rpm

# install postgres
yum install -y https://download.postgresql.org/pub/repos/yum/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-2.noarch.rpm
yum install -y postgresql95-server
su postgres -c '/usr/pgsql-9.5/bin/initdb -D /var/lib/pgsql/9.5/data'
/etc/init.d/postgresql-9.5 start
sleep 5

# mamonsu report
(mamonsu report | grep version | grep 'PostgreSQL 9.5') || exit 1

# export zabbix template
mamonsu -e /tmp/template.xml
grep 'pgsql\.uptime\[\]' /tmp/template.xml || exit 2 > /dev/null
grep 'system\.disk\.all_read' /tmp/template.xml || exit 2 > /dev/null

# export config
mamonsu -w /tmp/agent.conf

# start mamonsu and sleep
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
/etc/init.d/mamonsu restart
sleep 125

# metric log
grep utilization /tmp/localhost.log || exit 3
grep 'pgsql\.uptime' /tmp/localhost.log || exit 3

# all plugin alive
cat /var/log/mamonsu/agent.log
grep -i 'Plugin exception' /var/log/mamonsu/agent.log && exit 4
