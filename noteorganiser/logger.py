import logging


def create_logger(level='DEBUG'):
    """Defines a logger with optional level"""

    # Recover the associate value to the specified level
    level_value = 0
    for elem in dir(logging):
        if elem.find(level) != -1:
            exec("level_value = logging.%s" % elem)

    logger = logging.getLogger('simple_example')
    logger.name = "_name_"
    logger.setLevel(level_value)

    # create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_value)

    # create formatter
    formatter = logging.Formatter(
        "%(module) 17s: L%(lineno) 4s %(funcName) 25s"
        " | %(levelname) -10s  --> %(message)s")
        #"%(asctime)s %(module)s: L%(lineno) 4s %(funcName) 25s"
        #" | %(levelname) -10s  --> %(message)s")

    # add formatter to ch
    console_handler.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(console_handler)

    return logger
