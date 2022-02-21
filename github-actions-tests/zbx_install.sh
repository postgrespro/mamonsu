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
sudo mkdir 775 -p /docker/zabbix-docker/
cd /docker/zabbix-docker/ 2>&1 1>/dev/null
sudo wget https://github.com/zabbix/zabbix-docker/archive/refs/tags/${ZBX_VERSION}.zip
sudo unzip ${ZBX_VERSION}.zip
cd zabbix-docker-${ZBX_VERSION} 2>&1 1>/dev/null
echo "---> Setting up docker with Zabbix ${ZBX_VERSION}..."
# docker-compose dirty hack: it uses only file named 'docker-compose.yml'
yes | sudo cp docker-compose_v3_ubuntu_mysql_latest.yaml docker-compose.yml
docker-compose -f ./docker-compose.yml up -d
# wait for full set up
sleep 1m
