#!/bin/bash -ex

# 'mamonsu zabbix' tool testing

# Requirements:
# - running zabbix-server;
# - defined ZBX_ADDRESS ZBX_USER ZBX_PASSWORD, ZBX_VERSION;

# default parameters:
ZBX_ADDRESS="http://127.0.0.1/"
ZBX_VERSION="5.4"

for i in "$@"
do
case $i in
    --zbx-address=*)
    ZBX_ADDRESS="${i#*=}"
    shift
    ;;
    --zbx-version=*)
    ZBX_version="${i#*=}"
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

if [ ! -v ZBX_USER ];
then
    export ZBX_USER=Admin
fi
if [ ! -v ZBX_PASSWORD ];
then
    export ZBX_PASSWORD=zabbix
fi

echo "ZBX_ADDRESS=http://$ZBX_ADDRESS/, ZBX_USER=$ZBX_USER, ZBX_PASSWORD=$ZBX_PASSWORD"
OPTIONS="  --url=http://$ZBX_ADDRESS/ --user=$ZBX_USER --password=$ZBX_PASSWORD"

echo "Test with connect options: $OPTIONS "
## prepare
IFS='.' read -ra ZBX_VERSION_ARRAY <<<$ZBX_VERSION
ZBX_VERSION_MAJOR=${ZBX_VERSION_ARRAY[0]}
ZBX_VERSION_MINOR=${ZBX_VERSION_ARRAY[1]}

OLD_ZABBIX=" "
if  ((ZBX_VERSION_MAJOR <= 4))
then
  if  ((ZBX_VERSION_MINOR <= 2))
  then
    OLD_ZABBIX=" --old-zabbix "
  fi
fi

echo && echo "------> mamonsu zabbix version"
mamonsu zabbix version $OPTIONS
echo && echo "------> mamonsu zabbix export template"
mamonsu export template template.xml ${OLD_ZABBIX} --template-name="Mamonsu PostgreSQL"
# prepare
# create test host
echo && echo "------> mamonsu zabbix create host"
mamonsu zabbix $OPTIONS template export template.xml
mamonsu zabbix $OPTIONS host create "local-pg" $(mamonsu zabbix $OPTIONS hostgroup id "Linux servers") $(mamonsu zabbix $OPTIONS template id "Mamonsu PostgreSQL") "$(hostname -I | awk '{print $1}')"
mamonsu zabbix $OPTIONS host id "local-pg" | grep -x -E "[[:digit:]]+" || exit 11
rm -rf template.xml
sleep 5

# test 'mamonsu item'
echo && echo "------> mamonsu zabbix item error "
mamonsu zabbix $OPTIONS item error "local-pg"
echo && echo "------> mamonsu zabbix item lastvalue "
mamonsu zabbix $OPTIONS item lastvalue "local-pg"
echo && echo "------> mamonsu zabbix item lastclock"
mamonsu zabbix $OPTIONS item lastclock "local-pg"

# test 'mamonsu host'
echo && echo "------> mamonsu zabbix host list"
mamonsu zabbix $OPTIONS host list | grep "local-pg" || exit 11
echo && echo "------> mamonsu zabbix host show"
mamonsu zabbix $OPTIONS host show "local-pg" | grep "local-pg" || exit 11
echo && echo "------> mamonsu zabbix host id"
mamonsu zabbix $OPTIONS host id "local-pg" | grep -x -E "[[:digit:]]+" || exit 11
echo && echo "------> mamonsu zabbix host info templates"
mamonsu zabbix $OPTIONS host info templates $(mamonsu zabbix $OPTIONS host id "local-pg") | grep "local-pg" || exit 11
echo && echo "------> mamonsu zabbix host info hostgroups"
mamonsu zabbix $OPTIONS host info hostgroups $(mamonsu zabbix $OPTIONS host id "local-pg") | grep "local-pg" || exit 11
echo && echo "------> mamonsu zabbix host info graphs"
mamonsu zabbix $OPTIONS host info graphs $(mamonsu zabbix $OPTIONS host id "local-pg") | grep "local-pg"
echo && echo "------> mamonsu zabbix host info items"
mamonsu zabbix $OPTIONS host info items $(mamonsu zabbix $OPTIONS host id "local-pg")  | grep "local-pg"
echo && echo "------> mamonsu zabbix host create"
mamonsu zabbix $OPTIONS host create "test-create" $(mamonsu zabbix $OPTIONS hostgroup id "Linux servers") $(mamonsu zabbix $OPTIONS template id "Mamonsu PostgreSQL") "$(hostname -I | awk '{print $1}')"
mamonsu zabbix $OPTIONS host id "test-create" | grep -x -E "[[:digit:]]+" || exit 11
echo && echo "------> mamonsu zabbix host delete"
HOST_ID=$( mamonsu zabbix $OPTIONS host id "test-create" )
mamonsu zabbix $OPTIONS host delete ${HOST_ID} | grep "hostids.*${HOST_ID}" || exit 11

# test 'mamonsu hostgroup'
echo && echo "------> mamonsu zabbix hostgroup list"
mamonsu zabbix $OPTIONS hostgroup list | grep Templates || exit 11
echo && echo "------> mamonsu zabbix hostgroup show"
mamonsu zabbix $OPTIONS hostgroup show "Linux servers" | grep Linux || exit 11
echo && echo "------> mamonsu zabbix hostgroup id"
mamonsu zabbix $OPTIONS hostgroup id "Linux servers" | grep -x -E "[[:digit:]]+" || exit 11
echo && echo "------> mamonsu zabbix hostgroup create"
mamonsu zabbix $OPTIONS hostgroup create "Test servers"
mamonsu zabbix $OPTIONS hostgroup id "Test servers" | grep -x -E "[[:digit:]]+" || exit 11
echo && echo "------> mamonsu zabbix hostgroup delete"
HOSTGROUP_ID=$( mamonsu zabbix $OPTIONS hostgroup id "Test servers" )
mamonsu zabbix $OPTIONS hostgroup delete ${HOSTGROUP_ID} | grep "groupids.*${HOSTGROUP_ID}" || exit 11

# test 'mamonsu template'
echo && echo "------> mamonsu zabbix template list"
mamonsu zabbix $OPTIONS template list | grep "Mamonsu PostgreSQL" || exit 11
echo && echo "------> mamonsu zabbix template show"
mamonsu zabbix $OPTIONS template show "Mamonsu PostgreSQL" | grep "Mamonsu PostgreSQL" || exit 11
echo && echo "------> mamonsu zabbix template id"
mamonsu zabbix $OPTIONS template id "Mamonsu PostgreSQL" | grep -x -E "[[:digit:]]+" || exit 11
echo && echo "------> mamonsu zabbix template export"
mamonsu zabbix $OPTIONS template delete $(mamonsu zabbix $OPTIONS template id "Mamonsu PostgreSQL")
mamonsu export template template.xml ${OLD_ZABBIX} --template-name="mamonsu-zabbix"
mamonsu zabbix $OPTIONS template export template.xml
mamonsu zabbix $OPTIONS template id "mamonsu-zabbix" | grep -x -E "[[:digit:]]+" || exit 11
echo && echo "------> mamonsu zabbix template delete"
TEMPLATE_ID=$( mamonsu zabbix $OPTIONS template id "mamonsu-zabbix" )
mamonsu zabbix $OPTIONS template delete ${TEMPLATE_ID} | grep "templateids.*${TEMPLATE_ID}" || exit 11
rm -rf template.xml

exit 0
