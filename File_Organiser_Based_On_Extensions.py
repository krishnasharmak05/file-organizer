import logging
import os
import re
import shutil
import sys
import time

# import tkinter as tk
# from tkinter import filedialog
from tkinter import messagebox
import customtkinter as tk
from customtkinter import filedialog
import pyautogui

# import pyautogui
import TTSEngine_Handler as tts

sys.path.append("./assets")
from extensions_asset import folder_path_according_to_file_extension


# Refactor browse_files.


def browse_files() -> str:  # Might soon be unnecessary.
    folder: str = filedialog.askdirectory(
        initialdir=downloads_path, mustexist=True, title="Select a folder to sort"
    )
    if not folder:
        folder = warn()
    return folder


def warn() -> str:
    APP = True
    warning = f"Doing this chooses {downloads_path} as the folder to be organized. Do you want to continue?"
    warning_count = 0
    title = "Confirmation"
    choices = ["Let me choose a folder", "Yes", "No"]
    alertbox = tk.CTk()
    alertbox.withdraw()
    while True:    
        print("Here")
        response = pyautogui.confirm(warning, title, buttons=choices) 
        if response == "Let me choose a folder" and warning_count < 3:
            folder = filedialog.askdirectory(
                initialdir=downloads_path, mustexist=True, title="Select a folder to sort"
            )
            if not folder:
                warning_count += 1
            else:
                break
        elif response == "Let me choose a folder" and warning_count == 3:
            messagebox.showinfo(
                "Exiting Script",
                "You have already tried and cancelled 3 times. The script will now exit without running. Try again later.",
            )
            if alertbox and APP:
                alertbox.destroy()
                APP = False
                
            folder = "null"
            break
        elif response == "Yes":
            if alertbox and APP:
                alertbox.destroy()
                APP = False
                
            folder =  downloads_path
            break
        else:
            messagebox.showinfo(
                "Exiting Script", "The script has successfully exited without running now."
            )
            if alertbox and APP:
                alertbox.destroy()
                APP = False
                
            folder =  "null"
            break
        print("End")
    if APP:
        alertbox.mainloop()
    return folder


def get_files(folder: str) -> list[str]:
    file_list = [
        file
        for file in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, file))
    ]
    return file_list


def filetype_handler(folder: str, file: str) -> str | int:
    # Get the dict.values and based on dict indices, sort em. Reduce loops.
    new_folder_names_after_sorting = folder_path_according_to_file_extension.keys()
    try:
        extension = os.path.splitext(file)[1]
        for i in new_folder_names_after_sorting:
            if extension == None:
                logging.error(f"Error: No file extension found for file {file}.\n\n")
            elif extension in folder_path_according_to_file_extension[i]:
                destination_folder_path = folder + i
                return destination_folder_path
            elif i == "end":
                return -1
            else:
                logging.debug("No file extension matched until end of dictionary.\n\n")
    except Exception as e:
        logging.fatal(f"Failed on this file: {file}, with error: {e}\n\n")
        extension = None
    return -1


def file_organising_using_file_extensions(file_list: list[str], folder: str) -> None:
    cwd = os.getcwd()
    os.chdir(folder)
    log_file_path = os.path.join(os.path.expanduser(os.getcwd()), "logging.txt")
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    fail_count = 0
    unknown_files = []
    for file in file_list:
        if file == "logging.txt" or "DNM" in file:
            continue
        elif os.path.isdir(os.path.join(folder, file)):
            logging.info("Found a directory titled:\n" + file + "\n\n")
        else:
            destination_folder_path = filetype_handler(folder, file)
            if type(destination_folder_path) == str:
                if not os.path.exists(destination_folder_path):
                    os.makedirs(destination_folder_path)
                try:
                    shutil.move(file, destination_folder_path)
                except shutil.Error as e:
                    logging.error(e)
                    tts.engine.say("Shut-il Error: ")
                    tts.engine.say(e)
                    tts.engine.runAndWait()
            
            if destination_folder_path == -1:
                    logging.error("Unknown filetype for file:\n" + file + "\n\n")
                    fail_count += 1
                    unknown_files.append(file)

    tts.engine.stop()
    os.chdir(cwd)
    if fail_count == 1:
        time.sleep(1)
        tts.engine.say("Unknown file type for file:", unknown_files)
        tts.engine.runAndWait()
    elif fail_count > 1:
        time.sleep(1)
        tts_statement = f"Multiple files found, for which file type is unknown. Refer logging.txt in {folder} for more information."
        tts.engine.say(tts_statement)
        tts.engine.runAndWait()
    return None



downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

if __name__ == "__main__":

    folder = browse_files()
    if folder != "null":        
        file_list = get_files(folder)
        print(file_list)
        file_organising_using_file_extensions(file_list, folder)
