from typing import Any

from pyzabbix import ZabbixAPI

from config.config import Config
from src.utils.logger import LoggerClass

config = Config()


class ZabbixManager:
    def __init__(
            self,
            url: str = f"http://{config.ZABBIX_EXT_URL}/",
            username: str = config.ZABBIX_ADMIN_USER,
            password: str = config.ZABBIX_ADMIN_PASS,
    ):
        self.zbx = ZabbixAPI(url)
        self.zbx.login(username, password)
        self._logger = LoggerClass(self.__class__.__name__)

        self.host_ids = []
        self.hostgroup_ids = []
        self.template_ids = []

    @property
    def default_hostgroup_id(self) -> str:
        return self.get_hostgroup_id(config.DEFAULT_HOSTGROUP)

    @property
    def default_template_id(self) -> str:
        return self.get_template_id(config.DEFAULT_TEMPLATE)

    def remove_entities(self) -> None:
        for host_id in self.host_ids:
            self.delete_host(host_id)

        for hostgroup_id in self.hostgroup_ids:
            self.delete_hostgroup(hostgroup_id)

        for template_id in self.template_ids:
            self.delete_template(template_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove_entities()

    def get_host(self, hostname: str) -> dict[str, Any]:
        hosts = self.zbx.host.get(
            filter={"host": hostname},
            selectInterfaces=["ip"],
            selectGroups=["groupid"],
            selectParentTemplates=["templateid"]
        )
        return hosts[0] if hosts else None

    def get_host_id(self, hostname: str) -> str | None:
        host = self.get_host(hostname)
        return host.get("hostid") if host else None

    def list_hosts(self) -> list[dict[str, Any]]:
        return self.zbx.host.get(
            output=["hostid", "host"],
            selectGroups=["groupid"],
            selectParentTemplates=["templateid"]
        )

    def create_host(
            self,
            hostname: str,
            hostgroup_ids: list[str],
            template_ids: list[str],
            ip_address: str,
            port: int = 10050,
    ) -> str | None:
        self._logger.info(f"Creating host: {hostname}")
        interfaces = [{
            "type": 1,
            "main": 1,
            "useip": 1,
            "ip": ip_address,
            "dns": "",
            "port": str(port)
        }]

        groups = [{"groupid": gid} for gid in hostgroup_ids]
        templates = [{"templateid": tid} for tid in template_ids]
        data = {
            "host": hostname,
            "name": hostname,
            "interfaces": interfaces,
            "groups": groups,
            "templates": templates
        }

        host_id = self.zbx.host.create(data)['hostids'][0]
        self.host_ids.append(host_id)
        return host_id

    def delete_host(self, host_id: str) -> bool:
        try:
            self._logger.info(f"Deleting host ID: {host_id}")
            self.zbx.host.delete(host_id)
            return True
        except Exception as e:
            self._logger.warning(f"Failed to delete host: {str(e)}")
            return False

    def list_hostgroups(self) -> list[dict[str, Any]]:
        return self.zbx.hostgroup.get(output=["groupid", "name"])

    def get_hostgroup(self, name: str) -> dict[str, Any] | None:
        hostgroups = self.zbx.hostgroup.get(
            filter={"name": name},
            output=["groupid", "name"]
        )
        return hostgroups[0] if hostgroups else None

    def get_hostgroup_id(self, name: str) -> str | None:
        hostgroup = self.get_hostgroup(name)
        return hostgroup.get("groupid") if hostgroup else None

    def create_hostgroup(self, name: str) -> str | None:
        self._logger.info(f"Creating hostgroup: {name}")
        data = self.zbx.hostgroup.create({"name": name})
        hostgroup_id = data["groupids"][0]
        self.hostgroup_ids.append(hostgroup_id)
        return hostgroup_id

    def delete_hostgroup(self, group_id: str) -> bool:
        try:
            self._logger.info(f"Deleting hostgroup ID: {group_id}")
            self.zbx.hostgroup.delete(group_id)
            return True
        except Exception as e:
            self._logger.warning(f"Failed to delete hostgroup: {str(e)}")
            return False

    def get_template(self, name: str) -> dict[str, Any] | None:
        templates = self.zbx.template.get(filter={"host": name})
        return templates[0] if templates else None

    def get_template_id(self, name: str) -> str | None:
        template = self.get_template(name)
        return template.get("templateid") if template else None

    def list_templates(self) -> list[dict[str, Any]]:
        return self.zbx.template.get(output=["templateid", "host"])

    def delete_template(self, template_id: str) -> bool:
        try:
            self._logger.info(f"Deleting template ID: {template_id}")
            self.zbx.template.delete(template_id)
            return True
        except Exception as e:
            self._logger.warning(f"Failed to delete template: {str(e)}")
            return False
