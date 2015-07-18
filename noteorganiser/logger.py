from __future__ import unicode_literals
import logging


def create_logger(level='DEBUG', handler_type='stream'):
    """Defines a logger with optional level"""

    # Recover the associate value to the specified level
    level_value = getattr(logging, level, 0)

    logger = logging.getLogger('simple_example')
    logger.name = "_name_"
    logger.setLevel(level_value)

    # create the handler depengin on the desired type
    if handler_type == 'stream':
        handler = logging.StreamHandler()
    elif handler_type == 'file':
        handler = logging.FileHandler('log', mode='w')
    else:
        handler = logging.NullHandler()

    handler.setLevel(level_value)

    # create formatter
    formatter = logging.Formatter(
        "%(module) 17s: L%(lineno) 4s %(funcName) 25s"
        " | %(levelname) -10s  --> %(message)s")
        #"%(asctime)s %(module)s: L%(lineno) 4s %(funcName) 25s"
        #" | %(levelname) -10s  --> %(message)s")

    # add formatter to the console handler
    handler.setFormatter(formatter)

    # add the console handler to logger
    logger.addHandler(handler)

    return logger
