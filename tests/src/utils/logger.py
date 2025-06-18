import logging
from logging import DEBUG, Formatter, StreamHandler, basicConfig, getLogger
from sys import stdout
from typing import Union


class LoggerClass:
    def __init__(self, logger_name: str, level: Union[str, int] = "INFO"):
        console_handler = StreamHandler(stdout)
        console_handler.setLevel(DEBUG)

        formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        console_handler.setFormatter(formatter)

        basicConfig(
            encoding="utf-8",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[console_handler],
        )
        self.logger = getLogger(logger_name)
        self.set_level(level)

    def get_logger(self) -> logging.Logger:
        return self.logger

    def set_level(self, level: Union[str, int] = "INFO") -> None:
        self.logger.setLevel(level)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: Union[str, Exception]) -> None:
        self.logger.error(msg)
