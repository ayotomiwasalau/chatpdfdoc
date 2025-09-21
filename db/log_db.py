import os
from app.conf.log_conf import LogConf


class LogData:
    def __init__(self, log_conf: LogConf):
        self.log_file = log_conf.log_file

    def add_log(self, log: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log + "\n")

    def get_log(self):
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.readlines()
        except FileNotFoundError:
            return []
