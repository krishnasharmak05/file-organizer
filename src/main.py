import sys
import time
from pathlib import Path

from customtkinter import filedialog

from assets.animated_print import AnimatedPrint
from src.FileOrganizer import FileOrganizer


def get_folder()->str:
    initial_path: Path = Path.home() / "Downloads"
    if not initial_path.exists():
        initial_path = Path.home()
    folder: str = filedialog.askdirectory(
        initialdir=initial_path, mustexist=True, title="Select a folder to sort"
    )
    if not folder:
        AnimatedPrint.animated_print("No folder selected. Exiting safely...")
        time.sleep(2)
        sys.exit(0)
    return folder

def main():
    folder = get_folder()
    yaml_file = Path("config.yaml")
    engine = FileOrganizer(folder, yaml_file)
    engine.organize()


if __name__ == "__main__":
    main()
