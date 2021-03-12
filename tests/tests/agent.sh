#!/bin/bash -ex


# тест команд mamonsu agent *

# Требования:
# нет

mkdir -p /etc/mamonsu

cat <<EOF > /etc/mamonsu/agent.conf
[postgres]
host = 127.0.0.1
user = mamonsu_agent
database = mamonsu_agent
password = supersecret

[zabbix]
enabled = False


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


mamonsu &
sleep 1

mamonsu agent version
mamonsu agent metric-get system.disk.all_read[]
mamonsu agent metric-list

mamonsu agent -c /etc/mamonsu/agent.conf version
mamonsu agent metric-get system.disk.all_read[] -c /etc/mamonsu/agent.conf
mamonsu agent -c /etc/mamonsu/agent.conf metric-list

exit 0