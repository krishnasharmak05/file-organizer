from pathlib import Path
from fileorganizer.FileOrganizer import FileOrganizer
from fileorganizer.Status import Status
from tests.utils import LockedFile


def test_file_open_causes_failure(tmp_path):
    file_path = tmp_path / "locked_file.txt"
    file_path.write_text("hello")
    with LockedFile(file_path):
        organizer = FileOrganizer(tmp_path, Path("src/fileorganizer/config.yaml"))
        result = organizer.organize()

        assert result is False
        assert organizer.status == Status.FAILURE
        assert "WinError 32" in organizer.failure_reason or "locked" in organizer.failure_reason.lower()
