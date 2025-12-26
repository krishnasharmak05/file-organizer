import time
from typing import TextIO

import logging


# TODO: Redo all/most of it, as required based on the fact that it should now be producing a stream,
# that animatedly prints to console.
class AnimatedPrint(logging.Handler):
    def __text_generator(self, text: str):
        for i in text:
            yield i

    def animated_print(self, text:str):
        generated_text = self.__text_generator(text)
        try:
            while True:
                print(next(generated_text), end="", flush=True)
                time.sleep(0.05)
        except StopIteration:
            print()
            # return None
    
    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        self.animated_print(log_entry)
        
    # @classmethod
    # def progress_indicator(cls, percentage: int):
    #     completed = "▓"
    #     remaining = "░"

        ## Work from here...Not Complete.


if __name__ == "__main__":
    handler = AnimatedPrint()
    handler.animated_print("Hello, World!")
