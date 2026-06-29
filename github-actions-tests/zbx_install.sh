#!/bin/sh

# default parameters
ZBX_VERSION='5.4.10'

for parameter in "$@"
do
case $parameter in
    --zbx-version=*)
    ZBX_VERSION="${parameter#*=}"
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

echo "================================================================================================================="
sudo mkdir -m 775 -p /docker/zabbix-docker/
cd /docker/zabbix-docker/ 2>&1 1>/dev/null
sudo wget https://github.com/zabbix/zabbix-docker/archive/refs/tags/${ZBX_VERSION}.zip
sudo unzip ${ZBX_VERSION}.zip
cd zabbix-docker-${ZBX_VERSION} 2>&1 1>/dev/null
echo "---> Setting up docker with Zabbix ${ZBX_VERSION}..."
# docker-compose dirty hack: it uses only file named 'docker-compose.yml'
yes | sudo cp docker-compose_v3_alpine_mysql_latest.yaml docker-compose.yml

# Pin MySQL to 8.0.33 to avoid mysql_native_password deprecation in 8.0.34+
sudo sed -i 's/mysql:8\.0/mysql:8.0.33/g' docker-compose.yml

# Replace MYSQL_ROOT_PASSWORD_FILE with plain MYSQL_ROOT_PASSWORD to avoid:
# - "Secret file not found" in Zabbix 6.0+ web container (secret not mounted)
# - "Both X and X_FILE are set" in MySQL 8.0.46+ entrypoint
sudo sed -i 's/^\(MYSQL_ROOT_PASSWORD_FILE=.*\)/# \1/' env_vars/.env_db_mysql
sudo sed -i 's/^# MYSQL_ROOT_PASSWORD=$/MYSQL_ROOT_PASSWORD=root_pwd/' env_vars/.env_db_mysql
sudo sed -i 's/MYSQL_ROOT_PASSWORD_FILE=\/run\/secrets\/MYSQL_ROOT_PASSWORD/MYSQL_ROOT_PASSWORD=root_pwd/' compose_databases.yaml 2>/dev/null

docker-compose -f ./docker-compose.yml up -d

echo "---> Waiting for Zabbix ..."
WAITED=0
until curl -sf -X POST -H 'Content-Type: application/json' \
    -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":[],"id":1}' \
    http://localhost:80/api_jsonrpc.php 2>/dev/null | grep -q '"result"'; do
    sleep 5
    WAITED=$((WAITED + 5))
    if [ $WAITED -ge 300 ]; then
        echo "ERROR: Zabbix not ready after 300s"
        docker-compose -f ./docker-compose.yml ps
        docker-compose -f ./docker-compose.yml logs --tail=20
        exit 1
    fi
done
