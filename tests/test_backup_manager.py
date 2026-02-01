import os
import pytest
import shutil
from pathlib import Path

from fileorganizer.BackupManager import BackupManager
from fileorganizer.Status import Status

def create_file(path: Path, content: bytes):
    path.write_bytes(content)
    return path

def test_backup_creates_backup_and_hash(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    file = create_file(src / "a.txt", b"hello world")

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    backup = src / "Backups" / "a.txt.bak"
    hash_file = src / "Backups" / "Hashes" / "a.txt.bak.json"

    assert backup.exists()
    assert hash_file.exists()

def test_backup_preserves_contents(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    content = b"important data"
    create_file(src / "data.bin", content)

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    backup = src / "Backups" / "data.bin.bak"
    assert backup.read_bytes() == content


def test_backup_not_corrupted(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    create_file(src / "file.txt", b"abc123")

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    backup = src / "Backups" / "file.txt.bak"
    assert bm._is_file_corrupted(backup) is False


def test_backup_detects_corruption(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    create_file(src / "file.txt", b"original")

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    backup = src / "Backups" / "file.txt.bak"
    backup.write_bytes(b"tampered")

    assert bm._is_file_corrupted(backup) is True

def test_rollback_restores_deleted_file(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    original = create_file(src / "restore.txt", b"restore me")

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    original.unlink()
    assert not original.exists()

    bm.rollback()

    assert original.exists()
    assert original.read_bytes() == b"restore me"

def test_rollback_restores_modified_file(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    original = create_file(src / "file.txt", b"correct")

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    original.write_bytes(b"corrupted")

    bm.rollback()

    assert original.read_bytes() == b"correct"


def test_corrupted_backup_not_restored(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    original = create_file(src / "file.txt", b"safe")

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    backup = src / "Backups" / "file.txt.bak"
    backup.write_bytes(b"evil")

    original.unlink()
    bm.rollback()

    assert not original.exists()


@pytest.mark.skipif(os.name == "nt", reason="Symlink behavior differs on Windows")
def test_symlink_preserved(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    target = create_file(src / "target.txt", b"target")
    link = src / "link.txt"
    link.symlink_to(target)

    bm = BackupManager(src, classifier=None)
    bm.backup_all()

    backup_link = src / "Backups" / "link.txt.bak"

    assert backup_link.is_symlink()
    assert backup_link.readlink() == target
