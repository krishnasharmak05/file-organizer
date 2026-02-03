import portalocker

class LockedFile:
    def __init__(self, path):
        self.path = path
        self.f = None

    def __enter__(self):
        self.f = open(self.path, "r+")  # Windows + Linux both allow locking in r+ mode
        portalocker.lock(self.f, portalocker.LOCK_EX | portalocker.LOCK_NB)
        return self.f

    def __exit__(self, exc_type, exc, tb):
        if self.f is not None:
            portalocker.unlock(self.f)
            self.f.close()
