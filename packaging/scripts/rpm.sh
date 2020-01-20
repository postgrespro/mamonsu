#!/usr/bin/env bash

set -exu
set -o errexit
set -o pipefail


ulimit -n 1024

yum install -y -q tar make rpm-build python2-devel python-setuptools

cp -a /app/in /var/build
find /var/build -type d -exec chmod 0755 {} \;
find /var/build -type f -exec chmod 0644 {} \;

cd /var/build
make rpm

#mkdir -p /src/build/out/el/${DISTRIB_VERSION}
cp *.rpm /app/out/
