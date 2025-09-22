import os
from app.conf.log_conf import LogConf
import logging

class LogData:
    def __init__(self, log_conf: LogConf):
        self.log_file = log_conf.log_file
        self.logging = logging
        self.logging.basicConfig(
            filename=self.log_file,
            encoding="utf-8",
            filemode="a",
            format="{asctime} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
            level=logging.INFO
        )
    def add_log(self, log: str, level: str = "info"):
        if level == "info":
            self.logging.info(log)
        elif level == "debug":
            self.logging.debug(log)
        elif level == "warning":
            self.logging.warning(log)
        elif level == "error":
            self.logging.error(log)
        elif level == "critical":
            self.logging.critical(log)
        else:
            pass

    def get_log(self):
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            return []
