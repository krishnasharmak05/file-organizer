import logging
import os
import re
import shutil
import sys
from tkinter import filedialog
import TTSEngine_Handler as tts
sys.path.append("./File_Organiser_Based_On_Extensions/assets")
from extensions_asset import folder_path_according_to_file_extension #type: ignore



def browse_files() -> str:  # DEAD CODE
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    folder = filedialog.askdirectory(
        initialdir=downloads_path, title="Select a folder to sort"
    )
    if not folder:
        folder = downloads_path
    return folder


def get_files(folder: str) -> list[str]:
    file_list = os.listdir(folder)
    return file_list

def filetype_handler(folder: str, file: str):
    #pattern = r"\.(.*)"
    pattern = r"\.[a-zA-Z]{1,4}(?=[^\.]*$)"
    file_extensions = folder_path_according_to_file_extension.keys()
    temp = re.search(pattern, file)
    extension = temp.group() #type: ignore
    for i in file_extensions:
        if extension in folder_path_according_to_file_extension[i]:    
            filetype_path = folder + i
            return filetype_path
        elif i == "end":
            return -1
        else:
            pass


def file_organising_using_file_extensions(file_list: list[str], folder: str) -> None:
    cwd = os.getcwd()
    os.chdir(folder)
    log_file_path = os.path.join(os.path.expanduser(os.getcwd()), "logging.txt")
    logging.basicConfig(filename=log_file_path, level=logging.INFO)
    for file in file_list:
        if file == "logging.txt" or "DNM" in file:
            pass
        elif "." not in file:
            logging.info("Found a directory titled:\n" + file + "\n\n")
        else:
            filetype_path = filetype_handler(folder, file)
            if filetype_path == -1:
                logging.error("Unkown filetype for file:\n" + file + "\n\n")
                tts.engine.say("Un nown filetype for file:" + file ) # Line is written to match the phenetics of the engine. "Un nown" is not a spelling mistake.
                tts.engine.runAndWait()                
            elif not os.path.exists(filetype_path): #type: ignore
                os.makedirs(filetype_path) #type: ignore
            if filetype_path != -1:
                shutil.move(file, filetype_path) #type: ignore
            
    os.chdir(cwd)
    return None



folder = browse_files()
file_list = get_files(folder)
file_organising_using_file_extensions(file_list, folder)
