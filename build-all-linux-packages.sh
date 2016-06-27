#!/usr/bin/env bash

set -e
set -x

declare -a DISTRIBUTIVES_LIST=( "debian" "ubuntu" "centos" )
declare -a DEBIAN_VERSIONS=( "7" "8" )
declare -a DEBIAN_CODENAMES=( "wheezy" "jessie" )
declare -a UBUNTU_VERSIONS=( "12.04" "14.04" "15.10" "16.04" )
declare -a UBUNTU_CODENAMES=( "precise" "trusty" "wily" "xenial" )
declare -a CENTOS_VERSIONS=( "6" "7" )

type docker
type package_cloud

[ ! -z "$PACKAGECLOUD_TOKEN" ]

for DISTRIBUTIVE_NAME in "${DISTRIBUTIVES_LIST[@]}"
  do
    if [[ $DISTRIBUTIVE_NAME == "debian" ]]
      then
      COUNT="${#DEBIAN_VERSIONS[@]}"
      for (( INDEX=0; INDEX<=$(( $COUNT -1 )); INDEX++ ))
      do
        VERSION=${DEBIAN_VERSIONS[$INDEX]}
        CODENAME=${DEBIAN_CODENAMES[$INDEX]}
        docker run -v $(pwd):/var/tmp --rm debian:$VERSION bash -c "cd /var/tmp && \
            apt-get update -m && \
            apt-get install -y make dpkg-dev debhelper python-dev python-setuptools && \
            make deb"
        package_cloud push postgrespro/mamonsu/debian/$CODENAME *.deb
      done
    elif [[ $DISTRIBUTIVE_NAME == "ubuntu" ]]
      then
      COUNT="${#UBUNTU_VERSIONS[@]}"
      for (( INDEX=0; INDEX<=$(( $COUNT -1 )); INDEX++ ))
      do
        VERSION=${UBUNTU_VERSIONS[$INDEX]}
        CODENAME=${UBUNTU_CODENAMES[$INDEX]}
        docker run -v $(pwd):/var/tmp --rm ubuntu:$VERSION bash -c "cd /var/tmp && \
            apt-get update -m && \
            apt-get install -y make dpkg-dev debhelper python-dev python-setuptools && \
            make deb"
        package_cloud push postgrespro/mamonsu/ubuntu/$CODENAME *.deb
      done
    elif [[ $DISTRIBUTIVE_NAME == "centos" ]]
      then
      for DISTRIBUTIVE_VERSION in "${CENTOS_VERSIONS[@]}"
      do
        docker run -v $(pwd):/var/tmp --rm centos:$DISTRIBUTIVE_VERSION bash -c "cd /var/tmp && \
            yum install -y tar make rpm-build python2-devel python-setuptools && \
            make rpm"
        package_cloud push postgrespro/mamonsu/el/$DISTRIBUTIVE_VERSION *.rpm
      done
    fi
done
