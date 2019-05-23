import os
import logging
from logging.handlers import RotatingFileHandler
import json_formatter

__location__ = os.path.split(os.path.realpath(__file__))[0]

with open(os.path.join(__location__, '__version__')) as f:
    __version__ = f.read().strip()

def start(name, level=logging.DEBUG, filepath=None, handlerkw=None):
    logger = logging.getLogger()
    name = os.path.split(name)[-1]
    if filepath is None:
        pth = os.path.split(os.path.realpath(__file__))
        filepath = os.path.join(pth[0], 'logs')

    filename = os.path.join(filepath, name+'.log')
    screen_handler = logging.StreamHandler()
    
    pass_to_handler = dict(filename=filename,
                    maxBytes=int(5*10**6),
                    backupCount=200,
                    )
    handlerkw = {} if handlerkw is None else handlerkw

    pass_to_handler.update(handkerkw)

    file_handler = RotatingFileHandler(**pass_to_handler)

    formatter = json_formatter.JSONFormatter(
                ['levelname','module', 'funcName', 'lineno'])
    screen_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(screen_handler)
    logger.addHandler(file_handler)
    logger.setLevel(level)
