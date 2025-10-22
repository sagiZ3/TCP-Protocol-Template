import logging


RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"


class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_msg = super().format(record)
        if record.levelno == logging.ERROR:
            return RED + log_msg + RESET
        elif record.levelno == logging.WARNING:
            return YELLOW + log_msg + RESET
        elif record.levelno == logging.INFO:
            return GREEN + log_msg + RESET
        return log_msg


root_logger = logging.getLogger()
if root_logger.hasHandlers():
    root_logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(levelname)s: %(message)s"))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
