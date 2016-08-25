#!/bin/sh -ex

# test build
cp -a /var/tmp/ /root && cd /root
yum install -y tar make rpm-build python2-devel python-setuptools
make rpm && rpm -i mamonsu*.rpm

service mamonsu start
service mamonsu stop

# test uninstall
yum remove -y mamonsu
