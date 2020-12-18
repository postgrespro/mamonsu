#!/bin/bash -ex

/var/tmp/mamonsu/tests/local_install_mamonsu.sh
/var/tmp/mamonsu/tests/bootstrap.sh

###### test mamonsu zabbix *
mkdir /etc/mamonsu/
cp /var/tmp/mamonsu/packaging/conf/example.conf /etc/mamonsu/agent.conf
#ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.4 3.2 3.0"
ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.2 3.0"
for VER in $ZABBIX_DOCKER_VERSIONS
do
  IFS='.' read -ra VER_ARRAY <<<$VER
  VER_MAJOR=${VER_ARRAY[0]}
  VER_MINOR=${VER_ARRAY[1]}

  Z_PORT=":8080"
  if [[ "$VER" == "4.2" || "$VER" == "3.4" || "$VER" == "3.2"  ]]
  then
    Z_PORT=":80"
  fi
  export Z_URL="http://172.18.0.2$VER_MAJOR$VER_MINOR$Z_PORT"
  export Z_USER=Admin
  export Z_PASSWORD=zabbix
  export Z_VERSION=$VER
  echo "  Z_URL=$Z_URL,
  Z_USER=$Z_USER
  Z_PASSWORD=$Z_PASSWORD
  Z_VERSION=$Z_VERSION"
  /var/tmp/mamonsu/tests/zabbix.sh
done

exit 0