import shutil

from refactor.Logger import Logger


class BackupManager:
    def __init__(self, folder) -> None:
        self.folder = folder
        self.backup_folder = self.folder / "Backups"
        self.logger = Logger(self.folder / "Logs" / "backup_manager.log")

    def backup_all(self, files):
        #TODO: Check if the total disk space is large enough to store the backup, even temporarily.
        pass

    def rollback(self):
        pass

    def cleanup_backups(self):
        try:
            shutil.rmtree(self.backup_folder)
        except Exception as e:
            self.logger.error(f"Error occurred while cleaning up backups: {e}")
            raise
