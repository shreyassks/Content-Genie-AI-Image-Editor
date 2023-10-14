import logging
import os


class Logger:
    def __init__(self, log_level="INFO"):
        logging.basicConfig(
            format="%(asctime)s.%(msecs)03d %(levelname)05s %(module)s -"
            "%(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger()

        self.logger.setLevel(log_level)
        if os.environ.get("DEBUG", "false") == "true":
            self.logger.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))

    def get_logger(self):
        return self.logger


log_object = Logger()
logger = log_object.get_logger()
