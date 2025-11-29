import shutil
from pathlib import Path
from sys import orig_argv

from typing_extensions import List

from refactor.Exceptions import FileCorruptedException, InsufficientDiskSpace
from refactor.Logger import Logger


class BackupManager:
    def __init__(self, folder) -> None:
        self.folder = folder
        self.backup_folder = self.folder / "Backups"
        self.logger = Logger(self.folder / "Logs" / "backup_manager.log")

    def _get_files(self):
        return [child for child in self.folder.iterdir() if not child.is_dir()]

    def _is_file_corrupted(self, file):
        # TODO: Check by checking the file's sha256 hash against the recorded hash.
        pass

    def _record_sha256(self, file):
        pass

    def _copy_with_metadata(self, src: Path, dest: Path):
        with src.open("rb") as r, dest.open("wb") as w:
            shutil.copyfileobj(r, w)
        shutil.copystat(src, dest)

    def backup_all(self):
        self.backup_folder.mkdir(parents=True, exists_ok=True)
        files: List[Path] = self._get_files()
        remaining_free = shutil.disk_usage(self.backup_folder).free
        total_size = sum(file.stat().st_size for file in files)
        if remaining_free < total_size:
            self.logger.critical("Not enough disk space to backup all files.")
            raise InsufficientDiskSpace("Not enough disk space to backup all files.")
        self.logger.info("Starting backup...")
        for file in files:
            dest = self.backup_folder / f"{file.name}.bak"
            if dest.exists():
                # TODO: Implement the ability to prevent reorganization if backup for a file fails.
                self.logger.error(
                    f"Backup file {dest} already exists. "
                    "This file is not backed up, and hence it isn't reorgranized either."
                )

            try:
                self._record_sha256(
                    file
                )  # TODO: {file, file_hash} stored in a log folder for use in rollback.
                self._copy_with_metadata(file, dest)
                is_backup_copy_of_file_corrupted = self._is_file_corrupted(dest)
                if is_backup_copy_of_file_corrupted:
                    self._copy_with_metadata(file, dest)
                    if self._is_file_corrupted(dest):
                        # TODO: Maybe modify this to just ignore this file from backup and hence, reorganization?
                        self.logger.error(f"Backup file {dest} is corrupted.")
                        raise FileCorruptedException(f"Backup file {dest} is corrupted")
            except OSError as e:
                self.logger.critical(str(e), self.rollback)
        self.logger.info("Backup completed.")

    def rollback(self):
        # TODO: Rethink this. Ignore all comments in the next 4-5 lines, and the rewrite the code 
        # for this function entirely from scratch again.

        # Check if each file in self.folder exists in uncorrupted format.
        # If it does, delete from self.backup_folder
        # copy backup file back to self.folder
        for file in self.backup_folder.iterdir():
            if file.is_file() and file.suffix == ".bak":
                backup_file = file
                original_file = self.folder / backup_file.stem
                if original_file.exists() and not self._is_file_corrupted(
                    original_file
                ):
                    continue
                elif original_file.exists() and self._is_file_corrupted(original_file):
                    self.logger.warning(f"Original file {original_file} is corrupted.")
                elif backup_file.exists() and self._is_file_corrupted(backup_file):
                    self.logger.warning(f"Backup file {backup_file} is corrupted.")
                elif backup_file.exists():
                    self.logger.info(f"Rolling back {backup_file} to {original_file}")
                    shutil.move(backup_file, original_file)
                else:
                    self.logger.error(f"Backup file {backup_file} does not exist.")
        self.logger.info("Rollback completed.")

    def cleanup_backups(self):
        try:
            shutil.rmtree(self.backup_folder)
        except Exception as e:
            self.logger.error(f"Error occurred while cleaning up backups: {e}")
            raise
