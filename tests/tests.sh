#!/bin/bash -ex

pwd
cd tests
###### test mamonsu report *
./tests/report.sh

###### test mamonsu agent *
# ./tests/agent.sh                 !!! todo

###### test mamonsu bootstrap *
#./tests/bootstrap.sh
#
#
####### test mamonsu zabbix *
#mkdir -p /etc/mamonsu/              !!! todo
#sudo cp ../packaging/conf/example.conf /etc/mamonsu/agent.conf
##ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.4 3.2 3.0"
#ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.2 3.0"
#for VER in $ZABBIX_DOCKER_VERSIONS
#do
#  IFS='.' read -ra VER_ARRAY <<<$VER
#  VER_MAJOR=${VER_ARRAY[0]}
#  VER_MINOR=${VER_ARRAY[1]}
#
#  Z_PORT=":80$VER_MAJOR$VER_MINOR"
#
#  export Z_URL="http://192.168.26.228:$Z_PORT"
#  export Z_USER=Admin
#  export Z_PASSWORD=zabbix
#  export Z_VERSION=$VER
#  echo "  Z_URL=$Z_URL,
#  Z_USER=$Z_USER
#  Z_PASSWORD=$Z_PASSWORD
#  Z_VERSION=$Z_VERSION"
#  ./tests/zabbix.sh
#done

exit 0