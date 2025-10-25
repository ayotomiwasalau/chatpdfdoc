import os
from app.conf.log_conf import LogConf
import logging

class LogData:
    def __init__(self, log_conf: LogConf):
        self.log_file = log_conf.log_file
        logging.basicConfig(
            filename=self.log_file,
            encoding="utf-8",
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M",
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)

    def add_log(self, log: str, level: str = "info"):
        level = level.lower()
        if level == "info":
            self.logger.info(log)
        elif level == "debug":
            self.logger.debug(log)
        elif level == "warning":
            self.logger.warning(log)
        elif level == "error":
            self.logger.error(log)
        elif level == "critical":
            self.logger.critical(log)
        else:
            self.logger.info(log)

    def get_log(self):
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            return []
