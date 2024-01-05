# import sys
# sys.path.append("./File_Organiser_Based_On_Extensions/assets")
# from extensions_asset import folder_path_according_to_file_extension #type: ignore
# import re


# def filetype_handler(folder: str, file_list: list):
#     #pattern = r"\.[a-zA-Z]{1,4}"
#     pattern = r"\.[a-zA-Z]{1,4}(?=[^\.]*$)"

#     file_extensions = folder_path_according_to_file_extension.keys()
#     for filename in file_list:
#         temp = re.search(pattern, filename)
#         extension = temp.group() #type: ignore
#         print(extension)
#         for i in file_extensions:
#             if extension in folder_path_according_to_file_extension[i]:
#                 filetype = folder + i
#                 return filetype
#             elif i == "end":
#                 return -1



import pyttsx3

engine = pyttsx3.init()  # object creation

""" RATE"""
engine.setProperty("rate", 150)  # setting up new voice rate
rate = engine.getProperty("rate")

"""VOLUME"""
volume = engine.getProperty(
    "volume"
)
print(volume)  # printing current volume level
engine.setProperty("volume", 1.0)  # setting up volume level  between 0 and 1

"""VOICE"""
voices = engine.getProperty("voices")  # getting details of current voice
engine.setProperty(
    "voice", voices[1].id
)  # changing index, changes voices. 1 for female
engine.setProperty("rate", 175)  
rate = engine.getProperty("rate")
engine.say("Hello World!")
print(str(rate))
engine.say("My current speaking rate is " + str(rate))
engine.runAndWait()
engine.stop()