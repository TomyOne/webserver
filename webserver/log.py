import logging
class AnsiFore:
    KEEP = ""
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[39m"

    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_MAGENTA = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"
    BOLD_RESET = "\033[1;39m"


class AnsiStyle:
    BRIGHT = "\033[1m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    THIN = "\033[2m"
    NORMAL = "\033[22m"
    RESET_ALL = "\033[0m"


Fore = AnsiFore()
Style = AnsiStyle()

class LogFormatter(logging.Formatter):
    def __init__(self, *, include_timestamp: bool):
        fmt = "%(asctime)s " if include_timestamp else ""
        fmt += "%(levelname)s %(message)s"
        super().__init__(fmt=fmt, style="%")

    def format(self, record):
        formatted = super().format(record)
        prefix = {
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED,
        }.get(record.levelname, "")
        return f"{prefix}{formatted}{Style.RESET_ALL}"

def setup_log(
    debug: bool = False, quiet: bool = False, include_timestamp: bool = False
) -> None:
    import colorama

    if debug:
        log_level = logging.DEBUG
    elif quiet:
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)

    logging.getLogger("urllib3").setLevel(logging.WARNING)

    colorama.init()
    logging.getLogger().handlers[0].setFormatter(
        LogFormatter(include_timestamp=include_timestamp)
    )
