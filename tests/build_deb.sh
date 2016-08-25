#!/bin/sh -ex

# test build
cp -a /var/tmp/ /root && cd /var/tmp && (apt-get update || apt-get update || apt-get update)
(apt-get install -y make dpkg-dev debhelper python-dev python-setuptools || apt-get install -y make dpkg-dev debhelper python-dev python-setuptools)
make deb && dpkg -i mamonsu*.deb && cd /

service mamonsu start
service mamonsu stop

# test uninstall
apt-get purge -y mamonsu
