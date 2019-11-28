#!/usr/bin/env bash

set -exu
set -o errexit
set -o pipefail

ulimit -n 1024

yum install -y tar make rpm-build

mkdir -p /root/rpmbuild
cd /root/rpmbuild

cp -rv /app/in/packaging/rpm/* ./

cd /root/rpmbuild/SOURCES
sed -i "s/@DISTRIB@/${DISTRIB}/" mamonsu.repo

# build repo package
cd /root/rpmbuild/SPECS
rpmbuild -ba mamonsu_repo.spec

# copy artefact
cp -arv /root/rpmbuild/RPMS/noarch/*rpm /app/out/mamonsu-repo-$DISTRIB.noarch.rpm
