#!/bin/sh

# 'mamonsu export' tool testing

# default parameters:
PG_VERSION="14"

for i in "$@"
do
case $i in
    --pg-version=*)
    PG_VERSION="${i#*=}"
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

echo && echo
echo "================================================================================================================="
echo "---> Test MAMONSU EXPORT tool"
echo && echo

echo && echo "------> mamonsu export config mamonsu.conf --add-plugins"
mamonsu export config mamonsu.conf --add-plugins=/etc/mamonsu/plugins
file mamonsu.conf || exit 11
echo && echo "------> mamonsu export template template.xml --add-plugins"
mamonsu export template template.xml --add-plugins=/etc/mamonsu/plugins
file template.xml || exit 11
echo && echo "------> mamonsu export zabbix-parameters zabbix.conf --add-plugins=/etc/mamonsu/plugins --config=/etc/mamonsu/agent.conf --pg-version=${PG_VERSION}"
mamonsu export zabbix-parameters zabbix.conf --add-plugins=/etc/mamonsu/plugins --config=/etc/mamonsu/agent.conf --pg-version=${PG_VERSION}
file zabbix.conf || exit 11
echo && echo "------> mamonsu export zabbix-template zabbix_template.xml --template-name=\"mamonsu-zabbix\" --add-plugins=/etc/mamonsu/plugins --config=/etc/mamonsu/agent.conf"
mamonsu export zabbix-template zabbix_template.xml --template-name="mamonsu-zabbix" --add-plugins=/etc/mamonsu/plugins --config=/etc/mamonsu/agent.conf
file zabbix_template.xml || exit 11

rm -rf mamonsu.conf
rm -rf template.xml
rm -rf zabbix.conf
rm -rf scripts/
rm -rf zabbix_template.xml

exit 0