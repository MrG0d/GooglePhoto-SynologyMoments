import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GRAY, WHITE = range(9)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class PlainFormatter(logging.Formatter):
    FORMAT = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s (%(filename)s:%(lineno)d)'

    def __init__(self):
        logging.Formatter.__init__(self, self.FORMAT)  # , '%Y-%m-%d %H:%M:%S'

    def format(self, record: logging.LogRecord):
        return logging.Formatter.format(self, record)


class Logger(logging.Logger):

    def __init__(self, name):
        super().__init__(name)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(PlainFormatter())
        self.addHandler(stream_handler)

        stream_handler = logging.FileHandler('error.log')
        stream_handler.setLevel(logging.WARNING)
        stream_handler.setFormatter(PlainFormatter())
        self.addHandler(stream_handler)


