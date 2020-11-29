#!/bin/bash -ex

apt-get -y update
apt-get -y install python3
apt-get -y install python3-setuptools

cd /var/tmp/mamonsu
python3 setup.py build
python3 setup.py install

exit 0