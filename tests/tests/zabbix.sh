#!/bin/bash -ex

# тест команд mamonsu zabbix *

# Требования:
# наличие запущенного zabbix сервера и прописанные переменные окружения: Z_URL Z_USER Z_PASSWORD, Z_MAJOR_VERSION
# todo change and remove
#Z_URL=http://192.168.234.53/zabbix
#Z_USER=user
#Z_PASSWORD=111111

if [ ! -v Z_URL ];
then
    export Z_URL=localhost
fi
if [ ! -v Z_USER ];
then
    export Z_USER=Admon
fi
if [ ! -v Z_PASSWORD ];
then
    export Z_PASSWORD=zabbix
fi
if [ ! -v Z_VERSION ];
then
    export Z_VERSION=5.0
fi

echo "Z_URL=$Z_URL, Z_USER=$Z_USER, Z_PASSWORD=$Z_PASSWORD"
OPTIONS="  --url=$Z_URL --user=$Z_USER --password=$Z_PASSWORD"

# test 1 mamonsu zabbix template with
#mamonsu zabbix template list
#mamonsu zabbix template show <template name>
#mamonsu zabbix template id <template name>
#mamonsu zabbix template delete <template id>
#mamonsu zabbix template export <file>

echo "Test with connect options: $OPTIONS "
## prepare
IFS='.' read -ra Z_VERSION_ARRAY <<<$Z_VERSION
Z_VERSION_MAJOR=${Z_VERSION_ARRAY[0]}
Z_VERSION_MINOR=${Z_VERSION_ARRAY[1]}
echo Z_VERSION_MAJOR

OLD_ZABBIX=" "
if  ((Z_VERSION_MAJOR <= 4))
then
  if  ((Z_VERSION_MINOR <= 2))
  then
    OLD_ZABBIX=" --old-zabbix "
  fi
fi

mamonsu export template $OLD_ZABBIX template.xml | grep "Template for mamonsu has been saved as template.xml" || exit 11
mamonsu zabbix template export template.xml $OPTIONS
mamonsu zabbix template list $OPTIONS | grep PostgresPro-Linux || exit 11
mamonsu zabbix template show PostgresPro-Linux $OPTIONS | grep PostgresPro-Linux || exit 11
mamonsu zabbix template id PostgresPro-Linux $OPTIONS | grep -x -E "[[:digit:]]+" || exit 11
TEMPLATE_ID=`mamonsu zabbix template id PostgresPro-Linux $OPTIONS`
mamonsu zabbix template delete $TEMPLATE_ID $OPTIONS | grep "templateids.*$TEMPLATE_ID" || exit 11
mamonsu zabbix version  $OPTIONS
# test 2 mamonsu zabbix - Environment variables

export ZABBIX_URL=$Z_URL
export ZABBIX_USER=$Z_USER
export ZABBIX_PASSWD=$Z_PASSWORD

echo "Test with Environment variables: ZABBIX_URL=$ZABBIX_URL,  ZABBIX_USER=$ZABBIX_USER, ZABBIX_PASSWD=$ZABBIX_PASSWD"
mamonsu export template $OLD_ZABBIX template.xml | grep "Template for mamonsu has been saved as template.xml" || exit 11
mamonsu zabbix template export template.xml
mamonsu zabbix template list | grep PostgresPro-Linux || exit 11
mamonsu zabbix template show PostgresPro-Linux  | grep PostgresPro-Linux || exit 11
mamonsu zabbix template id PostgresPro-Linux  | grep -x -E "[[:digit:]]+" || exit 11
TEMPLATE_ID=`mamonsu zabbix template id PostgresPro-Linux`
mamonsu zabbix template delete $TEMPLATE_ID | grep "templateids.*$TEMPLATE_ID" || exit 11
mamonsu zabbix version

exit 0
