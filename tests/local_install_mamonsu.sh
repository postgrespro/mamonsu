#!/bin/bash -ex

apt-get -y update
apt-get -y install python3
apt-get -y install python3-setuptools

cd /var/tmp/mamonsu
python3 setup.py build
python3 setup.py install

mkdir -p /etc/mamonsu
touch /etc/mamonsu/agent.conf

mkdir -p /var/log/mamonsu
touch /var/log/mamonsu/agent.log
exit 0