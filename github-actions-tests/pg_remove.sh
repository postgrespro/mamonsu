#!/bin/sh

# default parameters:
OS="centos"
PACKAGE_MANAGER_REMOVE="sudo yum -y remove"
PG_VERSION="12"
PG_PATH="/usr/lib/postgresql/9.6/bin/"

for i in "$@"
do
case $i in
    --os=*)
    OS="${i#*=}"
    shift
    ;;
    --pmr=*)
    PACKAGE_MANAGER_REMOVE="${i#*=}"
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

echo "================================================================================================================="
echo "---> Remove PostgreSQL ${PG_VERSION}"

OS=${OS%:*}

if [ "${OS}" = "centos" ]; then
    PG_PATH="/usr/pgsql-${PG_VERSION}/bin/"
    sudo -u postgres ${PG_PATH}pg_ctl stop -D /pg${PG_VERSION}/data_slave_logical/
    sudo -u postgres ${PG_PATH}pg_ctl stop -D /pg${PG_VERSION}/data_slave_physical/
    sudo -u postgres ${PG_PATH}pg_ctl stop -D /pg${PG_VERSION}/data_master/
    sudo rm -rf /pg${PG_VERSION}/
    eval "${PACKAGE_MANAGER_REMOVE} pgdg-redhat-repo.noarch"
    eval "${PACKAGE_MANAGER_REMOVE} postgres*"
    sudo rm -rf /var/tmp/yum-root-*/pgdg-redhat-repo-latest.noarch.rpm
    sudo rm -rf /var/lib/yum/repos/x86_64/*/pgdg*
    sudo rm -rf /var/lib/pgsql
    sudo rm -rf /var/cache/yum/x86_64/*/pgdg*
    sudo rm -rf /usr/pgsql-${PG_VERSION}
elif [ "${OS}" = "ubuntu" ]; then
    PG_PATH="/usr/lib/postgresql/${PG_VERSION}/bin/"
    sudo -u postgres ${PG_PATH}pg_ctl stop -D /pg${PG_VERSION}/data_slave_logical/
    sudo -u postgres ${PG_PATH}pg_ctl stop -D /pg${PG_VERSION}/data_slave_physical/
    sudo -u postgres ${PG_PATH}pg_ctl stop -D /pg${PG_VERSION}/data_master/
    sudo rm -rf /pg${PG_VERSION}/
    eval "${PACKAGE_MANAGER_REMOVE} pgdg-redhat-repo.noarch"
    eval "${PACKAGE_MANAGER_REMOVE} postgres*"
    sudo rm -rf /etc/postgresql/
    sudo rm -rf /etc/alternatives/pg*
    sudo rm -rf /usr/local/pgsql
    sudo rm -rf /usr/lib/postgresql
    sudo rm -rf /var/lib/postgresql
fi
