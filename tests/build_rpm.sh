#!/bin/sh -ex

# test build
cp -a /var/tmp /root/mamonsu && cd /root/mamonsu
yum install -y tar make rpm-build python2-devel python-setuptools
make rpm && rpm -i mamonsu*.rpm

/etc/init.d/mamonsu start
sleep 5
/etc/init.d/mamonsu stop

# test uninstall
yum remove -y mamonsu
