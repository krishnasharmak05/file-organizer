from pathlib import Path
from typing_extensions import Dict, List

from refactor.Logger import Logger


class Classifier:
    def __init__(self, folder:Path, extension_map):
        self.folder = folder
        self.extension_map = extension_map
        self.logger = Logger(self.folder / "Logs" / "classifier.log")
        self.unknown = []

    def classify(self, files)->Dict[str, List[Path]]:
        # Implement classification logic here
        pass
