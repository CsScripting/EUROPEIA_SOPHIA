import logging
from colorama import Fore, Style, init as colorama_init

# Initialize colorama for automatic style reset
colorama_init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'WARNING': Fore.YELLOW,
        'INFO': Fore.GREEN,
        'DEBUG': Fore.BLUE,
        'CRITICAL': Fore.RED,
        'ERROR': Fore.RED
    }

    def format(self, record):
        log_message = super().format(record)
        return self.COLORS.get(record.levelname, Fore.WHITE) + log_message 