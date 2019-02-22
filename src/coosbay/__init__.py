import os
import logging
from logging.handlers import TimedRotatingFileHandler
import json_formatter

__location__ = os.path.split(os.path.realpath(__file__))[0]

with open(os.path.join(__location__, '__version__')) as f:
    __version__ = f.read().strip()

def start(name, level=logging.DEBUG, filepath=None):
    logger = logging.getLogger()
    name = os.path.split(name)[-1]
    if filepath is None:
        pth = os.path.split(os.path.realpath(__file__))
        filepath = os.path.join(pth[0], 'logs')

    filename = os.path.join(filepath, name+'.log')
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
