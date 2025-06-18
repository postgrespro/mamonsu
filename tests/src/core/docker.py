import logging

import docker

from config.constants.containers import ContainersEnum


class DockerManager:
    def __init__(self, container_name: ContainersEnum) -> None:
        self._client = docker.from_env()
        self._container_name = container_name
        self._container = self._client.containers.get(container_name)
        self._logger = logging.getLogger(__name__)

    def __call__(self, command: str) -> tuple[int, str]:
        return self._run_in_container(command)

    @property
    def env_vars(self) -> dict[str, str]:
        env_dict = {}
        for env_line in self._container.attrs['Config']['Env']:
            if '=' in env_line:
                key, value = env_line.split('=', 1)
                env_dict[key] = value
        return env_dict

    @property
    def ip_address(self) -> str | None:
        networks = self._container.attrs['NetworkSettings']['Networks']
        return list(networks.values())[0]['IPAddress']

    @property
    def hostname(self) -> ContainersEnum:
        return self._container_name

    def stop(self) -> None:
        try:
            self._container.stop()
        except docker.errors.NotFound:
            pass

    def remove(self) -> None:
        try:
            self._container.remove()
        except docker.errors.NotFound:
            pass

    def remove_image(self) -> None:
        try:
            self._client.images.remove(image_id=self._container.image)
        except docker.errors.NotFound:
            pass

    def _run_in_container(self, command: str) -> tuple[int, str]:
        self._logger.info(f"Command: {command}")
        exit_code, output = self._container.exec_run(["/bin/bash", "-c", command])
        formatted_output = output.decode('utf-8').strip()
        self._logger.info(f"Exited with code {exit_code}, output: {formatted_output}")
        return exit_code, formatted_output
