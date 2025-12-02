import logging
import sys
from assets.animated_print import AnimatedPrint
from typing_extensions import Callable


class Logger:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(AnimatedPrint())) # Make this work
        file_handler = logging.FileHandler(self.log_file_path)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def critical(self, message, cleanup: Callable | None = None):
        """
        Logs a critical message and forces the program to exit.
        """
        self.logger.critical("The program has encountered a critical error.")
        self.logger.critical(message)
        if cleanup:
            cleanup()
        self.logger.critical("The program will now exit.")
        sys.exit(0)

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)
