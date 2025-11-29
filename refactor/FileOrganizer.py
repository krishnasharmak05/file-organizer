import shutil
from logging import CRITICAL, DEBUG, ERROR, FATAL, INFO, WARN, WARNING
from pathlib import Path

from typing_extensions import Dict, List

from refactor.BackupManager import BackupManager
from refactor.Classifier import Classifier
from refactor.Exceptions import UnknownLoggingLevelException
from refactor.Logger import Logger
from refactor.Status import Status


class FileOrganizer:
    def __init__(self, folder: str, extension_map: Dict[str, str]) -> None:
        self.folder = Path(folder)
        self.classifier = Classifier(self.folder, extension_map)
        self.logger = Logger(self.folder / "Logs" / "file_organizer.log")
        self.backup_manager = BackupManager(self.folder)
        self.status = Status.IN_PROGRESS
        self.failure_reason = ""

    def organize(self):
        files = self._get_files()
        try:
            self.backup_manager.backup_all(files)
            self._organize_files(files)
        except Exception as e:
            self.status = Status.FAILURE
            self.logger.error(f"Error occurred during organization: {e}")
            self.failure_reason = str(e)
            self._log_details()
            self.backup_manager.rollback()
        else:
            self.backup_manager.cleanup_backups()
            self.status = Status.SUCCESS
            self._log_details()
        finally:
            self._log_summary()

    def _get_files(self) -> List[Path]:
        return [
            p
            for p in self.folder.iterdir()
            if p.is_file() and p.name not in ("logging.txt",)
        ]

    def _organize_files(self, files: List[Path]) -> None:
        sorted_files: Dict[str, List[Path]] = self.classifier.classify(files)
        for folder, _files in sorted_files.items():
            folder_path = Path(self.folder / folder)
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
            for file_path in _files:
                destination = folder_path / file_path.name
                try:
                    shutil.move(str(file_path), str(destination))
                except Exception as e:
                    self.logger.error(
                        f"Error moving file {file_path} to {destination}: {e}"
                    )
                    raise

    def _log_details(self, details, level):
        log = None
        if level == ERROR:
            log = self.logger.error
        elif level == INFO:
            log = self.logger.info
        elif level == WARN:
            log = self.logger.warn
        elif level == CRITICAL:
            log = self.logger.critical
        elif level == DEBUG:
            log = self.logger.debug
        else:
            raise UnknownLoggingLevelException(
                "Level of Logging is unknown. This error should not have happened!"
            )
        log(details)

    def _log_summary(self):
        if self.status == Status.SUCCESS:
            self.logger.info(
                f"Files Organized Successfully at {self.folder}."
                f"Logs can be found at {self.folder / 'Logs'}"
            )
        elif self.status == Status.FAILURE:
            self.logger.error(
                f"File organization FAILED at  {self.folder}.\n"
                f"Reason: {self.failure_reason}\n."
                f"Logs can be found at {self.folder / 'Logs'}"
            )
