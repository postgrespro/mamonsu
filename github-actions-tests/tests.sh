#!/bin/sh

# default parameters:
OS="centos:7"
PG_VERSION="14"

for i in "$@"
do
case $i in
    --os=*) # OS type:version
    OS="${i#*=}"
    shift
    ;;
    --pg-version=*)
    PG_VERSION="${i#*=}"
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

echo && echo
echo "================================================================================================================="
echo "---> Run tests"
echo "---> OS: ${OS}"
echo "---> PG: ${PG_VERSION}"
echo && echo

# OS-dependent variables
PACKAGE_MANAGER_INSTALL="sudo yum -y install"
PACKAGE_MANAGER_REMOVE="sudo yum -y remove"
REPO="sudo yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm"

if [ "${OS}" = "centos:7" ]; then
    # install and set up components missing in docker image (sudo, wget, bc, unzip)
    yum clean all
    yum update -y
    yum install -y sudo
    PACKAGE_MANAGER_INSTALL="sudo yum -y install"
    PACKAGE_MANAGER_REMOVE="sudo yum -y remove"
    eval "${PACKAGE_MANAGER_INSTALL} wget"
    eval "${PACKAGE_MANAGER_INSTALL} bc"
    eval "${PACKAGE_MANAGER_INSTALL} unzip"
    REPO=${PACKAGE_MANAGER_INSTALL}" https://download.postgresql.org/pub/repos/yum/reporpms/EL-"$(echo ${OS} | sed -r 's/^[^0-9]*([0-9]+).*/\1/')"-x86_64/pgdg-redhat-repo-latest.noarch.rpm"

    # run tests
    sudo bash /mamonsu/github-actions-tests/pg_install.sh --os="${OS}" --pmi="${PACKAGE_MANAGER_INSTALL}" --repo="${REPO}" --pg-version="${PG_VERSION}"

elif [ "${OS}" = "centos:8" ]; then
    # install and set up components missing in docker image (sudo, wget, bc, unzip)
    dnf update -y
    dnf install -y sudo
    PACKAGE_MANAGER_INSTALL="sudo dnf -y install"
    PACKAGE_MANAGER_REMOVE="sudo dnf -y remove"
    eval "${PACKAGE_MANAGER_INSTALL} wget"
    eval "${PACKAGE_MANAGER_INSTALL} bc"
    eval "${PACKAGE_MANAGER_INSTALL} unzip"
    REPO=${PACKAGE_MANAGER_INSTALL}" https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm; sudo dnf -qy module disable postgresql"

    # run tests
    sudo bash /mamonsu/github-actions-tests/pg_install.sh --os="${OS}" --pmi="${PACKAGE_MANAGER_INSTALL}" --repo="${REPO}" --pg-version="${PG_VERSION}"

elif [ "${OS%:*}" = "ubuntu" ]; then
    # install and set up components missing in docker image (sudo, wget, bc, unzip, lsb-release, gnupg, tzdata)
    apt-get clean && apt-get update && apt-get install -y sudo
    PACKAGE_MANAGER_INSTALL="sudo apt-get -y install"
    PACKAGE_MANAGER_REMOVE="sudo apt-get -y remove"
    eval "${PACKAGE_MANAGER_INSTALL} wget"
    eval "${PACKAGE_MANAGER_INSTALL} bc"
    eval "${PACKAGE_MANAGER_INSTALL} unzip"
    eval "${PACKAGE_MANAGER_INSTALL} lsb-release"
    eval "${PACKAGE_MANAGER_INSTALL} gnupg"
    echo 1 > input.txt
    echo 1 >> input.txt
    eval "${PACKAGE_MANAGER_INSTALL} tzdata < input.txt"
    ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime
    echo Europe/Moscow > /etc/timezone
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7FCC7D46ACCC4CF8

    # add info about PG repo for ubuntu
    REPO="sudo sh -c 'echo \"deb http://apt.postgresql.org/pub/repos/apt \$(lsb_release -cs)-pgdg main\" > /etc/apt/sources.list.d/pgdg.list'; wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - ; sudo apt-get update"

    # run tests
    sudo bash /mamonsu/github-actions-tests/pg_install.sh --os="${OS}" --pmi="${PACKAGE_MANAGER_INSTALL}" --repo="${REPO}" --pg-version="${PG_VERSION}"

fi
