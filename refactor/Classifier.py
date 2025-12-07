from pathlib import Path

from typing_extensions import Dict, List
from yaml import YAMLError, safe_load

from refactor.Logger import Logger


class Classifier:
    def __init__(self, folder: Path, yaml_file: Path) -> None:
        self.folder: Path = folder
        self.extension_map: Dict[str, List[str]] = {}
        self.logger: Logger = Logger(self.folder / "Logs" / "classifier.log")
        self.unknown: List[Path] = []
        self.known: List[Path] = []
        self._set_extension_map(yaml_file)

    def _invert(self, config):
        inverted = {}
        for folder, extensions in config.items():
            for ext in extensions:
                inverted[ext] = folder
        return inverted

    def _set_extension_map(self, yaml_file: Path):
        try:
            with open(yaml_file, "r") as f:
                data = safe_load(f)
                if not isinstance(data, dict):
                    raise ValueError(
                        "Extension map must be a mapping (folder → extensions)"
                    )
                self.extension_map = self._invert(data)
        except FileNotFoundError:
            self.logger.critical(f"Extension map file not found: {yaml_file}")
        except YAMLError:
            self.logger.critical(
                f"Invalid YAML format in extension map file: {yaml_file}"
            )
        except Exception as e:
            self.logger.critical(
                f"An error occurred while loading extension map file: {e}"
            )

    def classify(self, files: List[Path]) -> Dict[str, List[Path]]:
        folder_path_dict = {}
        for file in files:
            folder_path = self.extension_map.get(file.suffix)
            if not folder_path:
                self.unknown.append(file)
                continue
            folder_path_dict.setdefault(folder_path, []).append(file)
            self.known.append(file)
        return folder_path_dict