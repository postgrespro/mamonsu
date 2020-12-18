#!/bin/bash -ex

if [ ! -v ZABBIX_DOCKER_VERSIONS ];
then
    #export ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.4 3.2 3.0"
    export ZABBIX_DOCKER_VERSIONS="5.2 5.0 4.4 4.2 4.0 3.2 3.0"
fi
# !!!! zabbix 4.4 имеет порт 80, остальные 8080
#ZABBIX_DOCKER_VERSIONS="4.4"

docker run -it -d \
  --name pg_for_zabbix \
  --ip 172.18.0.7 \
  --net network-local-tests \
  --hostname pg_for_zabbix \
  -e POSTGRES_PASSWORD="111111" \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  postgres:13 /bin/bash /docker-entrypoint.sh -c max_connections=200
sleep 3

docker exec -d -i pg_for_zabbix psql -U postgres -c 'create user zabbix superuser'
docker exec -d -i pg_for_zabbix psql -U postgres -c 'create database zabbix owner zabbix'
for VER in $ZABBIX_DOCKER_VERSIONS
do
  VER2="${VER/./_}"
  IFS='.' read -ra VER_ARRAY <<<$VER
  VER_MAJOR=${VER_ARRAY[0]}
  VER_MINOR=${VER_ARRAY[1]}
  docker exec -d -i pg_for_zabbix psql -U postgres -c "create database zabbix_$VER2 owner zabbix"
  sleep 1
  docker run \
    --name="zabbix-server-pgsql_$VER2" \
    --ip="172.18.0.1$VER_MAJOR$VER_MINOR" \
    --net network-local-tests \
    --hostname="zabbix-server-pgsql_$VER2" \
    -e DB_SERVER_HOST="pg_for_zabbix" \
    -e DB_SERVER_DBNAME="server_$VER2" \
    -e POSTGRES_USER="zabbix" \
    -e POSTGRES_DB="zabbix_$VER2" \
    -e PHP_TZ="Europe/Moscow" \
    -d zabbix/zabbix-server-pgsql:alpine-$VER-latest

  sleep 1
  docker run \
    --name="zabbix-web-apache-pgsql_$VER2" \
    --net="network-local-tests" \
    --ip="172.18.0.2$VER_MAJOR$VER_MINOR" \
    -e DB_SERVER_HOST="pg_for_zabbix" \
    -e ZBX_SERVER_HOST="zabbix-server-pgsql_$VER2" \
    -e DB_SERVER_DBNAME="zabbix_$VER2" \
    -e POSTGRES_DB="zabbix_$VER2" \
    -e POSTGRES_USER="zabbix" \
    --restart unless-stopped \
    -e PHP_TZ="Europe/Moscow" \
    -d zabbix/zabbix-web-apache-pgsql:alpine-$VER-latest
done
exit 0


# docker exec -it -i pg_for_zabbix psql -U postgres -c '\l'
# docker exec -it -i pg_for_zabbix psql -U postgres -c '\du'
# docker exec -it zabbix-web-apache-pgsql_5.0 bash