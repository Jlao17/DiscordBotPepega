import logging


class LoggingFormatter(logging.Formatter):
    grey = "\x1b[38;5;251m"
    yellow = "\x1b[38;5;220m"
    red = "\x1b[38;5;203m"
    bold_red = "\x1b[31;1m"
    cyan = "\x1b[36m"
    reset = "\x1b[0m"
    format = "[%(filename)s:%(lineno)d] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger(level=logging.DEBUG):
    if len(logging.getLogger().handlers) > 0:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = LoggingFormatter()
    ch.setFormatter(formatter)

    root_logger.addHandler(ch)
