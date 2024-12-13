import time

class AnimatedPrint:
    def __text_generator(text):
        for i in text:
            yield i
    
    @classmethod
    def animated_print(self, text):
        generated_text = self.__text_generator(text)
        try:
            while True:
                print(next(generated_text), end="", flush=True)
                time.sleep(0.05)
        except StopIteration:
            print()
            return None
        
    
    @classmethod
    def progress_indicator(self, percentage: int):
        completed = "▓"
        remaining = "░"

        ## Work from here...Not Complete.
        

if __name__ == "__main__":
    AnimatedPrint.animated_print("Hello, World!")