#!/bin/bash -ex
## для тестов
export DOCKER_HOST=ssh://apopov@zabbixs

docker stop -t 1 $(docker ps -a -q) | true
sleep 1
docker rm -f $(docker ps -a -q ) | true
sleep 1
docker network rm network-zabbixs | true
sleep 1

docker network create --driver=bridge --subnet=172.18.0.0/16 network-zabbixs

if [ ! -v ZABBIX_DOCKER_VERSIONS ];
then
    export ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.2 3.0"
    #export ZABBIX_DOCKER_VERSIONS="5.2"
fi
#ZABBIX_DOCKER_VERSIONS="4.4"

docker run -it -d \
  --name pg_for_zabbix \
  --ip 172.18.0.7 \
  --net network-zabbixs \
  --hostname pg_for_zabbix \
  -e POSTGRES_PASSWORD="111111" \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  --restart unless-stopped \
  postgres:13 /bin/bash /docker-entrypoint.sh -c max_connections=200
sleep 5

docker exec -d -i pg_for_zabbix psql -U postgres -c 'create user zabbix superuser'
sleep 1
docker exec -d -i pg_for_zabbix psql -U postgres -c 'create database zabbix owner zabbix'
sleep 3

for VER in $ZABBIX_DOCKER_VERSIONS
do
  Z_PORT="8080"
  if [[ "$VER" == "4.2" || "$VER" == "3.4" || "$VER" == "3.2"  ]]
  then
    Z_PORT="80"
  fi


  VER2="${VER/./_}"
  IFS='.' read -ra VER_ARRAY <<<$VER
  VER_MAJOR=${VER_ARRAY[0]}
  VER_MINOR=${VER_ARRAY[1]}
  docker exec -d -i pg_for_zabbix psql -U postgres -c "create database zabbix_$VER2 owner zabbix"
  sleep 1
  docker run \
    --name="zabbix-server-pgsql_$VER2" \
    --ip="172.18.0.1$VER_MAJOR$VER_MINOR" \
    --net network-zabbixs \
    --hostname="zabbix-server-pgsql_$VER2" \
    -e DB_SERVER_HOST="pg_for_zabbix" \
    -e DB_SERVER_DBNAME="server_$VER2" \
    -e POSTGRES_USER="zabbix" \
    -e POSTGRES_DB="zabbix_$VER2" \
    -e PHP_TZ="Europe/Moscow" \
    -p 200$VER_MAJOR$VER_MINOR:10051 \
    --restart unless-stopped \
    -d zabbix/zabbix-server-pgsql:alpine-$VER-latest

  sleep 1

  docker run \
    --name="zabbix-web-apache-pgsql_$VER2" \
    --net="network-zabbixs" \
    --ip="172.18.0.2$VER_MAJOR$VER_MINOR" \
    -e DB_SERVER_HOST="pg_for_zabbix" \
    -e ZBX_SERVER_HOST="zabbix-server-pgsql_$VER2" \
    -e DB_SERVER_DBNAME="zabbix_$VER2" \
    -e POSTGRES_DB="zabbix_$VER2" \
    -e POSTGRES_USER="zabbix" \
    --restart unless-stopped \
    -e PHP_TZ="Europe/Moscow" \
    -p 80$VER_MAJOR$VER_MINOR:$Z_PORT \
    --restart unless-stopped \
    -d zabbix/zabbix-web-apache-pgsql:alpine-$VER-latest

    echo "http port 80$VER_MAJOR$VER_MINOR"
    echo "zabbix server port 200$VER_MAJOR$VER_MINOR"
done
exit 0


# docker exec -it -i pg_for_zabbix psql -U postgres -c '\l'
# docker exec -it -i pg_for_zabbix psql -U postgres -c '\du'
# docker exec -it zabbix-web-apache-pgsql_5.0 bash