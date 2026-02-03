# TODO: Add Logging to all operations. - Will be added in upcoming versions.
import json
import shutil
import sys
import time
from hashlib import sha256
from pathlib import Path

from typing_extensions import List

from fileorganizer.Exceptions import (
    FileNotFoundException,
    InsufficientDiskSpace,
)
from fileorganizer.Logger import Logger


class BackupManager:
    """
    Handles backups, cleanups after the file organisation and rollbacks, in case of a failure.

    @property folder: Path - The path to the folder to organize.
    @property backup_folder: Path - The path to the backup folder.
    @property hash_folder: Path - The path to the hash folder.
    @property logger: Logger - The logger instance.
    """

    def __init__(self, folder, classifier, dereference_symlinks: bool = False) -> None:
        self.folder: Path = folder
        self.backup_folder: Path = self.folder / "Backups"
        self.hash_folder: Path = self.backup_folder / "Hashes"
        self.classifier = classifier
        self.logger: Logger = Logger(self.folder / "Logs" / "backup_manager.log")
        self.transaction_log: Path = self.logger.details_file_path
        self.follow_symlinks: bool = dereference_symlinks

    def _get_files(self) -> list[Path]:
        """
        Returns a list of files in the folder.

        @return list[Path] - A list of files in the folder.
        """
        return [child for child in self.folder.iterdir() if not child.is_dir()]

    # TODO: Checking for file corruption fails. Fix the logic
    def _is_file_corrupted(self, file: Path) -> bool:
        """
        Checks if a file is corrupted by checking the file's sha256 hash against the recorded hash.

        @param file: Path - The path to the file to check.

        @return bool - Returns True if the file is corrupted, False otherwise.
        """
        hash_file = self.hash_folder / f"{file.name}.json"

        if not hash_file.exists():
            self.logger.error(f"Hash file for {file.name} does not exist.")
            return True
        try:
            with hash_file.open("r", encoding="utf-8") as f:
                hash_json = json.load(f)

            recorded_hash = hash_json["sha256"]
            recorded_size = hash_json["size"]

            if file.stat().st_size != recorded_size:
                return True
            current_hash = self._get_hash(file)
            return current_hash != recorded_hash

        except (OSError, KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to validate hash for {file.name}: {e}")
            return True

    def _get_hash(self, path: Path, chunk_size: int = 1024 * 1024) -> str:
        """
        Hashes a file using the SHA256 algorithm.

        @param path: Path - The path to the file to hash.
        @param chunk_size: int (optional) - The size of the chunks to read for hashing.

        @return str - The SHA256 hash of the file
        """
        h = sha256()
        with path.open("rb") as f:
            for block in iter(lambda: f.read(chunk_size), b""):
                h.update(block)
        hash = h.hexdigest()
        return hash

    def _record_sha256(self, backup_file: Path, original_file: Path) -> Path:
        """
        Record the SHA256 hash of a file in a json file.

        @param path: Path - The path to the file to hash.
        @param chunk_size: int (optional) - The size of the chunks to read for hashing in Bytes. Defaults to 1MB.

        Data is stored in the following format:
            hash_json = {
                "file": path.name,
                "size": path.stat().st_size,
                "sha256": hash,
                "timestamp": int(time.time()),
            }

        @return Path - The path to the json file containing the hash information
        """
        hash_value = self._get_hash(backup_file)
        hash_json = {
            "original_name": original_file.name,
            "backup_name": backup_file.name,
            "size": backup_file.stat().st_size,
            "sha256": hash_value,
            "timestamp": int(time.time()),
        }
        self.hash_folder.mkdir(parents=True, exist_ok=True)
        hash_file = self.hash_folder / f"{backup_file.name}.json"
        hash_file.write_text(json.dumps(hash_json), encoding="utf-8")
        return hash_file

    # def _copy_with_metadata(self, src: Path, dest: Path) -> None:
    #     """
    #     Copies a file with its metadata.

    #     Args:
    #         src (Path): The source file path.
    #         dest (Path): The destination file path.
    #     """
    #     with src.open("rb") as r, dest.open("wb") as w:
    #         shutil.copyfileobj(r, w)
    #     shutil.copystat(src, dest)

    def backup_all(self) -> None:
        """
        Backup all files in the source folder to the backup folder.
        """
        self.backup_folder.mkdir(parents=True, exist_ok=True)
        files: List[Path] = self._get_files()
        remaining_free = shutil.disk_usage(self.backup_folder).free
        # Hash size = int(total number of files in the folder)* size(hash_json)
        hash_json_example = {
            "file": "example.txt",
            "size": 1048576,
            "sha256": "031edd7d41651593c5fe5c006fa5752b37fddff7bc4e843aa6af0c950f4b9406",
            "timestamp": 1732163942,
        }
        total_expected_size = sum(file.stat().st_size for file in files) + (
            len(files) * sys.getsizeof(json.dumps(hash_json_example))
        )
        if remaining_free < total_expected_size:
            # TODO: figure out whether to put logger.critical or error, and whether to implement the exception
            self.logger.error("Not enough disk space to backup all files.")
            raise InsufficientDiskSpace("Not enough disk space to backup all files.")
        self.logger.info("Starting backup...")
        for file in files:
            if file.suffix == ".lnk":
                continue
            dest = self.backup_folder / f"{file.name}.bak"
            if dest.exists():
                self.logger.error(f"File {file.name} already exists in backup folder.")
                continue
            try:
                # self._copy_with_metadata(file, dest)
                shutil.copy2(file, dest, follow_symlinks=self.follow_symlinks)
                self._record_sha256(dest, file)

                if self._is_file_corrupted(dest):
                    raise IOError(f"Backup file {dest.name} is corrupted.")

            except Exception as e:
                self.logger.critical(e)
                self.rollback()
                raise
        self.logger.info("Backup Complete...")

    def rollback(self) -> None:
        """
        Rollback all files in the backup folder to the source folder.
        Remember to remove logging handler
        """
        # Follows the principle of Atomicity.
        self.logger.warning("Starting rollback...")

        if not self.backup_folder.exists():
            self.logger.warning("No Backup folder found. Nothing to rollback.")
            return

        for backup_file in self.backup_folder.glob("*.bak"):
            if backup_file.suffix != ".bak":
                continue

            if self._is_file_corrupted(backup_file):
                self.logger.error(f"Corrupted backup detected: {backup_file}")
                continue

            original_path = self.folder / backup_file.stem

            try:
                if original_path.exists():
                    original_path.unlink()
                shutil.copy2(backup_file, original_path, follow_symlinks=False)
                self.logger.info(f"Restored {original_path}")
            except OSError as e:
                self.logger.critical(f"Rollback failed for {original_path}: {e}")

        self.logger.info("Rollback Complete.")

    def cleanup_backups(self) -> None:
        """
        Cleans up the backup folder by removing all files and directories within it.
        """
        self.logger.info("Cleaning up backups...")
        try:
            if self.backup_folder.exists:
                shutil.rmtree(self.backup_folder)
            else:
                raise FileNotFoundException("Backup folder does not exist.")
        except Exception as e:
            self.logger.critical(
                "File Organization successful, but some files may remain in the backup folder."
                + "You can delete them manually."
                + f"This error occurred while cleaning up backups: {e}",
            )
        finally:
            self.logger.cleanup()
