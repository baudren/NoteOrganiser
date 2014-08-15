"""
.. module:: configuration
    :synopsys: Recover the list of existing notebooks

.. moduleauthor:: Benjamin Audren <benjamin.audren@gmail.com>
"""
import os
from constants import EXTENSION


def initialise(logger):
    """
    Platform independent recovery of the main folder and notebooks

    """
    # Platform independent recovery of the home directory. It is always put as
    # a hidden folder, '.noteorganiser', in the unix tradition.
    home = os.path.expanduser("~")
    main = os.path.join(home, '.noteorganiser')

    # Recursively search the main folder for notebooks or folders of notebooks
    # It also checks if the folder ".noteorganiser" exists, and creates it
    # otherwise.
    notebooks = search_folder_recursively(logger, main)

    # Return both the path to the folder where it is stored, and the list of
    # notebooks
    return main, notebooks


def search_folder_recursively(logger, main):
    notebooks = []
    if os.path.isdir(main):
        logger.info("Main folder existed already")
        # If yes, check if there are already some notebooks
        for elem in os.listdir(main):
            if os.path.isfile(os.path.join(main, elem)):
                if elem.find(EXTENSION) != -1:
                    logger.info("Found the file %s as a valid notebook" % elem)
                    notebooks.append(elem)
            elif os.path.isdir(os.path.join(main, elem)):
                temp = search_folder_recursively(
                    logger, os.path.join(main, elem))
                if temp:
                    notebooks.append((
                        os.path.join(main, elem), temp))
    else:
        logger.info("Main folder non-existant: creating it now")
        os.mkdir(main)
    return notebooks


if __name__ == "__main__":
    from logger import create_logger
    logger = create_logger()
    print(initialise(logger))
