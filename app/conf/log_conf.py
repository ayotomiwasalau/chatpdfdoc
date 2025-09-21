from app.conf.config import Config

class LogConf:
    def __init__(self, config: Config) -> None:
        self.log_file = config.log_file
