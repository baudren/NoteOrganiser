"""
.. module:: configuration
    :synopsys: Recover the list of existing notebooks

.. moduleauthor:: Benjamin Audren <benjamin.audren@gmail.com>
"""
import os


def initialise(logger):
    """
    Platform independent recovery of the main folder and notebooks

    """
    # Initialise an empty list of notebooks
    notebooks = []

    # Platform independent recovery of the home directory. It is always put as
    # a hidden folder, '.noteorganiser', in the unix tradition.
    home = os.path.expanduser("~")
    main = os.path.join(home, '.noteorganiser')

    # Check if the folder ".noteorganiser" exists
    if os.path.isdir(main):
        logger.info("Main folder existed already")
        # If yes, check if there are already some notebooks
        for elem in os.listdir(main):
            if os.path.isfile(os.path.join(main, elem)):
                logger.info("Found the file %s as a valid notebook" % elem)
                notebooks.append(elem)
    else:
        logger.info("Main folder non-existant: creating it now")
        os.mkdir(main)

    # Return both the path to the folder where it is stored, and the list of
    # notebooks
    return main, notebooks

if __name__ == "__main__":
    from logger import create_logger
    logger = create_logger()
    print(initialise(logger))
