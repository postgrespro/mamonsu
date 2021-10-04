#!/bin/sh

# 'mamonsu agent' tool testing

echo && echo
echo "================================================================================================================="
echo "---> Test MAMONSU AGENT tool"
echo && echo

echo && echo "------> mamonsu agent version"
mamonsu agent version
echo && echo "------> mamonsu agent metric-get system.disk.all_read[]"
mamonsu agent metric-get system.disk.all_read[]
echo && echo "------> mamonsu agent metric-list"
mamonsu agent metric-list

echo && echo "------> mamonsu agent -c /etc/mamonsu/agent.conf version"
mamonsu agent -c /etc/mamonsu/agent.conf version
echo && echo "------> mamonsu agent metric-get system.disk.all_read[] -c /etc/mamonsu/agent.conf"
mamonsu agent metric-get system.disk.all_read[] -c /etc/mamonsu/agent.conf
echo && echo "------> mamonsu agent -c /etc/mamonsu/agent.conf metric-list"
mamonsu agent -c /etc/mamonsu/agent.conf metric-list

kill `jobs -p`
exit 0
