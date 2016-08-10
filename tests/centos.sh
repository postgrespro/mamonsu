#/bin/sh -ex

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

# test metric send to log
cat <<EOF > /etc/mamonsu/agent.conf
[zabbix]
address = 127.0.0.1
[metric_log]
directory = /tmp
EOF
/etc/init.d/mamonsu restart && sleep 10
grep utilization /tmp/localhost.log
grep 'pgsql\.uptime' /tmp/localhost.log

# test uninstall
yum remove -y mamonsu
