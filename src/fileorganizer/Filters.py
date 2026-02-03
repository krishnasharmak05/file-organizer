import logging


class DetailFilter(logging.Filter):
    def __init__(self, allow_detail: bool) -> None:
        super().__init__()
        self.allow_detail = allow_detail

    def filter(self, record: logging.LogRecord) -> bool:
        is_detail = getattr(record, "detail", False)
        return is_detail if self.allow_detail else not is_detail


class ConsoleFilter(logging.Filter):
    def __init__(self, allow_console: bool) -> None:
        super().__init__()
        self.allow_console = allow_console
    
    def filter(self,record: logging.LogRecord) -> bool:
        return True