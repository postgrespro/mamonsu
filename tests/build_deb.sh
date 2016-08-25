#!/bin/bash -ex

# test build
cp -a /var/tmp /root/mamonsu && pushd /root/mamonsu
apt-get update || apt-get update || apt-get update
(apt-get install -y make dpkg-dev debhelper python-dev python-setuptools || apt-get install -y make dpkg-dev debhelper python-dev python-setuptools)
make deb && dpkg -i mamonsu*.deb && cd /

/etc/init.d/mamonsu start
sleep 5
/etc/init.d/mamonsu stop

# test uninstall
apt-get purge -y mamonsu
