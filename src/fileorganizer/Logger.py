import logging
from pathlib import Path

from fileorganizer.Filters import DetailFilter
from fileorganizer.Exceptions import FatalError
from typing_extensions import Callable

from assets.animated_print import AnimatedPrint


class Logger:
    def __init__(self, log_file_path: Path):
        self.log_file_path = log_file_path
        self.details_file_path = log_file_path.parent / "Details.log"

        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file_path.touch(exist_ok=True)
        self.details_file_path.touch(exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{log_file_path.stem}")
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # Console Handler
        self.console_handler = AnimatedPrint()
        self.console_handler.setFormatter(formatter)
        self.console_handler.addFilter(DetailFilter(allow_detail=False))
        self.console_handler.setLevel(logging.INFO)
        
        # Main File Handler
        self.file_handler = logging.FileHandler(self.log_file_path)
        self.file_handler.setFormatter(formatter)
        self.file_handler.addFilter(DetailFilter(allow_detail=False))
        self.file_handler.setLevel(logging.INFO)
        
        # Details File Handler
        self.details_handler = logging.FileHandler(self.details_file_path)
        self.details_handler.setFormatter(formatter)
        self.details_handler.addFilter(DetailFilter(allow_detail=True))
        self.details_handler.setLevel(logging.INFO)
        
        # Add Handlers
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.details_handler)

    def info(self, message):
        self.logger.info(message)

    def detail(self, message):
        # Done: Make this go into a separate Details.log file, which should be accessible by backup manager as well.
        # Backup manager will use this file to check the transactions before rollback.
        self.logger.info(message, extra={"detail": True})

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
        return FatalError(message) # FIXME: Implement proper error handling

    def debug(self, message):
        self.logger.debug(message)

    def error(self, message):
        self.logger.error(message)

    def cleanup(self):
        for handler in list(self.logger.handlers):
            handler.close()
            self.logger.removeHandler(handler)

        
