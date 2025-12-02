import time
from typing import TextIO


# TODO: Redo all/most of it, as required based on the fact that it should now be producing a stream,
# that animatedly prints to console.
class AnimatedPrint(TextIO):
    @classmethod
    def __text_generator(cls, text: str):
        for i in text:
            yield i

    @classmethod
    def animated_print(cls, text):
        generated_text = cls.__text_generator(text)
        try:
            while True:
                print(next(generated_text), end="", flush=True)
                time.sleep(0.05)
        except StopIteration:
            print()
            # return None

    @classmethod
    def progress_indicator(cls, percentage: int):
        completed = "▓"
        remaining = "░"

        ## Work from here...Not Complete.


if __name__ == "__main__":
    AnimatedPrint.animated_print("Hello, World!")
