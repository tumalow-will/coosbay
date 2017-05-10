import os
import logging
from logging.handlers import TimedRotatingFileHandler
import json_formatter


def start(filename=None, level=logging.DEBUG):
    logger = logging.getLogger()
    if filename is None:
        pth = os.path.split(os.path.realpath(__file__))
        filename = os.path.join(pth[0], 'logs', pth[1]+'.log')

    screen_handler = logging.StreamHandler()
    file_handler = TimedRotatingFileHandler(
                    filename=filename,
                    when='midnight'
                    )

    formatter = json_formatter.JSONFormatter(
                ['levelname','module', 'funcName', 'lineno'])
    screen_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(screen_handler)
    logger.addHandler(file_handler)
    logger.setLevel(level)
