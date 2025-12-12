import shutil
from pathlib import Path

from typing_extensions import Dict, List

from fileorganizer.BackupManager import BackupManager
from fileorganizer.Classifier import Classifier
from fileorganizer.Logger import Logger
from fileorganizer.Status import Status


class FileOrganizer:
    def __init__(self, folder: str, extension_map_path: Path) -> None:
        self.folder = Path(folder)
        self.classifier = Classifier(self.folder, extension_map_path)
        self.logger = Logger(self.folder / "Logs" / "fileorganizer.log")
        self.backup_manager = BackupManager(self.folder)
        self.status = Status.IN_PROGRESS
        self.failure_reason = ""

    def organize(self) -> bool:
        files = self._get_files()
        try:
            self.backup_manager.backup_all()
            self._organize_files(files)
        except Exception as e:
            self.status = Status.FAILURE
            self.logger.error(f"Error occurred during organization: {e}")
            self.failure_reason = str(e)
            self.backup_manager.rollback()
        else:
            self.logger.info(f"Files Organized Successfully at {self.folder}.")
            self.backup_manager.cleanup_backups()
            self.status = Status.SUCCESS
        finally:
            self._log_summary()

        return self.status == Status.SUCCESS

    def _get_files(self) -> List[Path]:
        return [
            p
            for p in self.folder.iterdir()
            if p.is_file() and p.name not in ("logging.txt",)
        ]

    def _organize_files(self, files: List[Path]) -> None:
        sorted_files: Dict[str, List[Path]] = self.classifier.classify(files)
        self.classifier.cleanup()
        for folder, _files in sorted_files.items():
            folder_path = Path(self.folder / folder)
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
            for file_path in _files:
                destination = folder_path / file_path.name
                try:
                    shutil.move(str(file_path), str(destination))
                    self.logger.detail(f"Moved {file_path} to {destination}")
                except Exception as e:
                    self.logger.error(
                        f"Error moving file {file_path} to {destination}: {e}"
                    )
                    raise

    def _log_summary(self):
        if self.status == Status.SUCCESS:
            self.logger.info(f"Logs can be found at {self.folder / 'Logs'}")
            self.logger.cleanup()
        elif self.status == Status.FAILURE:
            self.logger.error(
                f"File organization FAILED at  {self.folder}.\n"
                f"Reason: {self.failure_reason}\n."
                f"Logs can be found at {self.folder / 'Logs'}"
            )
