class UnknownLoggingLevelException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InsufficientDiskSpace(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class FileCorruptedException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class FileNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class FatalError(Exception):
    pass