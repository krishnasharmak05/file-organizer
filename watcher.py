from assets.animated_print import AnimatedPrint
animated_print = AnimatedPrint.animated_print

from customtkinter import filedialog
from watchdog.events import FileMovedEvent # Add whatever is required here.
from watchdog.observers import Observer
import time

def watcher():
    animated_print("Want a folder to be monitored and organized dynamically?")
    animated_print("This script will do that for you.")
    animated_print("Please choose a folder to monitor.")
    time.sleep(0.5)
    folder = filedialog.askdirectory( title="Select a folder to be monitored")
    observer = Observer()
    event = observer.schedule(event_handler=FileMovedEvent, path=folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
            if event: # Work on this... Not complete.
                print(f"Event detected: {event}")
                break
    finally:
        observer.stop()
        observer.join()

    animated_print("Done")

if __name__ == "__main__":
    watcher()