import shutil
import time
from pathlib import Path

import pytest
from yaml import safe_load

from fileorganizer.FileOrganizer import FileOrganizer  # pyright: ignore[reportMissingImports]

# TODO: Switch to using pytest's tmp_path instead of manually creating a folder
class TestIntegration:
    def invert(self, config):
        inverted = {}
        for folder, extensions in config.items():
            for ext in extensions:
                inverted[ext] = folder
        return inverted

    @pytest.fixture
    def config(self):
        with open("src/fileorganizer/config.yaml", "r") as file:
            return safe_load(file)

    @pytest.fixture
    def config_path(self):
        return "src/fileorganizer/config.yaml"

    @pytest.fixture
    def path_to_test_folder(self):
        return Path("./test_folder")

    @pytest.mark.usefixtures("path_to_test_folder")
    def create_dummy_folder_as_placeholder(self, path_to_test_folder: Path):
        if not path_to_test_folder.exists():
            path_to_test_folder.mkdir(parents=True, exist_ok=True)
            time.sleep(5)
            path_to_test_folder.rmdir()

    @pytest.mark.usefixtures("path_to_test_folder", "config_path")
    def sort_files(self, path_to_test_folder, config_path) -> bool:
        organizer = FileOrganizer(path_to_test_folder, config_path)
        return organizer.organize()

    @pytest.mark.usefixtures("path_to_test_folder")
    def remove_created_files(self, path_to_test_folder):
        if path_to_test_folder.exists():
            shutil.rmtree(path_to_test_folder)
            assert not path_to_test_folder.exists()
        else:
            assert False

    @pytest.mark.usefixtures("path_to_test_folder", "config")
    def build_random_files(self, path_to_test_folder: Path, config):
        complete = True
        if not complete:
            self.create_dummy_folder_as_placeholder(path_to_test_folder)
            assert False
        else:
            if not path_to_test_folder.exists():
                path_to_test_folder.mkdir(parents=True, exist_ok=True)
            for folder, extensions in config.items():
                for ext in extensions:
                    file_name = f"{folder}_{int(time.time())}"
                    file_path = path_to_test_folder / f"{file_name}{ext}"
                    file_path.touch()
            assert True

    @pytest.mark.usefixtures("path_to_test_folder", "config", "config_path")
    def test_sorted_files(self, path_to_test_folder, config, config_path):
        self.build_random_files(path_to_test_folder, config)
        assert self.sort_files(path_to_test_folder, config_path)
        self.remove_created_files(path_to_test_folder)
