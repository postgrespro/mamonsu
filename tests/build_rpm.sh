#!/bin/sh -ex

# test build
cp -a /var/tmp /root/mamonsu && pushd /root/mamonsu
yum install -y tar make rpm-build python3-devel python3-setuptools rpmlint
rpmlint packaging/rpm/SPECS/mamonsu.spec
make rpm && rpm -i mamonsu*.rpm

/etc/init.d/mamonsu start
sleep 5
/etc/init.d/mamonsu stop

# test uninstall
yum remove -y mamonsu
