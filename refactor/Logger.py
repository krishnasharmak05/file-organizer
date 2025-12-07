import logging
import sys
from pathlib import Path

from typing_extensions import Callable

from assets.animated_print import AnimatedPrint


class Logger:
    def __init__(self, log_file_path: Path):
        self.log_file_path = log_file_path
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file_path.touch(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(AnimatedPrint()))  # Make this work
        self.file_handler = logging.FileHandler(self.log_file_path)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def critical(self, message, cleanup: Callable | None = None):
        """
        Logs a critical message and forces the program to exit.
        """
        self.logger.critical(message)
        if cleanup:
            cleanup()
        self.logger.critical("The program will now exit safely.")
        sys.exit(500)

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)
    
    def cleanup(self):
        self.logger.removeHandler(self.file_handler)