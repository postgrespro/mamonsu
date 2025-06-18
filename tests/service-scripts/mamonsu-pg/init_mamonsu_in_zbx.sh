#!/bin/sh

INIT_MARKER="/app/.init_done"
if [ ! -f "$INIT_MARKER" ]; then
  echo "[INFO] Exporting templates"
  mamonsu export template template.xml
  mamonsu zabbix template export template.xml

  echo "[INFO] Adding host in Zabbix"
  mamonsu zabbix host create "$(hostname)" \
    "$(mamonsu zabbix hostgroup id "Zabbix servers")" \
    "$(mamonsu zabbix template id "Mamonsu PostgreSQL Linux")" \
    "$(getent hosts "$(hostname)" | awk '{print $1}')"
  service mamonsu start

  echo "[INFO] Waiting for host to appear in Zabbix"
  sleep 5
  touch "$INIT_MARKER"
else
  echo "[INFO] Initialization already done. Skipping Mamonsu setup"
fi

