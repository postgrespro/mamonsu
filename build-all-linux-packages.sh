#!/usr/bin/env bash

set -e
set -x

declare -a DISTRIBUTIVES_LIST=("debian" "ubuntu" "centos")
declare -a DEBIAN_VERSIONS=( "7" "8" )
declare -a UBUNTU_VERSIONS=( "12.04" "14.04" "15.10" "16.04" )
declare -a CENTOS_VERSIONS=( "6" "7" )

type docker

for DISTRIBUTIVE_NAME in "${DISTRIBUTIVES_LIST[@]}"
  do
    if [[ $DISTRIBUTIVE_NAME == "debian" ]]
      then
      for DISTRIBUTIVE_VERSION in "${DEBIAN_VERSIONS[@]}"
      do
        docker run -v $(pwd):/var/tmp --rm debian:$DISTRIBUTIVE_VERSION bash -c "cd /var/tmp && \
            apt-get update -m && \
            apt-get install -y make dpkg-dev debhelper python-dev python-setuptools && \
            make deb"
      done
    elif [[ $DISTRIBUTIVE_NAME == "ubuntu" ]]
      then
      for DISTRIBUTIVE_VERSION in "${UBUNTU_VERSIONS[@]}"
      do
        docker run -v $(pwd):/var/tmp --rm ubuntu:$DISTRIBUTIVE_VERSION bash -c "cd /var/tmp && \
            apt-get update -m && \
            apt-get install -y make dpkg-dev debhelper python-dev python-setuptools && \
            make deb"
      done
    elif [[ $DISTRIBUTIVE_NAME == "centos" ]]
      then
      for DISTRIBUTIVE_VERSION in "${CENTOS_VERSIONS[@]}"
      do
        docker run -v $(pwd):/var/tmp --rm centos:$DISTRIBUTIVE_VERSION bash -c "cd /var/tmp && \
            yum install -y tar make rpm-build python2-devel python-setuptools && \
            make rpm"
      done
    fi
done
