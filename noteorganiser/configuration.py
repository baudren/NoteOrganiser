"""
.. module:: configuration
    :synopsys: Recover the list of existing notebooks

.. moduleauthor:: Benjamin Audren <benjamin.audren@gmail.com>
"""
from __future__ import unicode_literals
import os
from noteorganiser.constants import EXTENSION

from PySide import QtCore

def initialise(logger):
    """
    Platform independent recovery of the main folder and notebooks

    """
    # Platform independent recovery of the home directory. It is always put as
    # a hidden folder, '.noteorganiser', in the unix tradition.
    home = os.path.expanduser("~")
    main = os.path.join(home, '.noteorganiser')

    settings = QtCore.QSettings("audren", "NoteOrganiser")
    if settings.contains("display_empty"):
        if settings.value("display_empty") == "true":
            display_empty = True
        else:
            display_empty = False
    else:
        display_empty = True

    # Recursively search the main folder for notebooks or folders of notebooks
    # It also checks if the folder ".noteorganiser" exists, and creates it
    # otherwise.
    # folders will contain all the non-empty folders in the main. The method
    # search_folder_recursively will be called again when the user wants to
    # explore also the contents of this folder
    notebooks, folders = search_folder_recursively(logger, main, display_empty)

    # Return both the path to the folder where it is stored, and the list of
    # notebooks
    return main, notebooks, folders


def search_folder_recursively(logger, main, display_empty):
    """
    Search the main folder for notebooks and folders with notebooks

    Note that the returned notebooks and folders are flat (that is, folders is
    not a list that then contains all the subnotebooks. They are discarded, and
    only loaded if the folder is then clicked on).

    Parameters
    ----------
    logger : logging module instance

    main : str
        folder to search

    display_empty : bool
        determines whether to return empty folders or not
    """
    notebooks, folders = [], []
    if os.path.isdir(main):
        logger.info("Main folder existed already")
        # If yes, check if there are already some notebooks
        for elem in os.listdir(main):
            if os.path.isfile(os.path.join(main, elem)):
                # If it is a valid file, append it to notebooks
                if elem[-len(EXTENSION):] == EXTENSION:
                    logger.info("Found the file %s as a valid notebook" % elem)
                    notebooks.append(elem)
            elif os.path.isdir(os.path.join(main, elem)):
                # Otherwise, check the folder for valid files, and append it to
                # folders in case there are some inside, or if display_empty is
                # set to True (by default).
                # If the folder is hidden (linux convention, with a leading
                # dot), ignore. TODO also determines if it is hidden as far as
                # Windows is concerned
                if elem[0] != '.':
                    temp, _ = search_folder_recursively(
                        logger, os.path.join(main, elem), display_empty)
                    if temp or display_empty:
                        folders.append(os.path.join(main, elem))
    else:
        logger.info("Main folder non-existant: creating it now")
        os.mkdir(main)
    return notebooks, folders


class Information(object):
    """storage of information across the application"""

    def __init__(self, logger, root, notebooks, folders):
        # Store the main variables
        # This is a reference to the global logger
        self.logger = logger
        # root stores the absolute path to the noteorganiser folder. It should
        # point to ~/.noteorganiser on a Unix type machine, and I don't know
        # where on a Windows.
        self.root = root
        # level stores the current path in the root folder (still in absolute
        # path, though)
        self.level = root

        # notebooks is the list of notebooks files (ending with EXTENSION),
        # found in "level". Folders contains the list of non-empty, non-hidden
        # folders in this directory.
        self.notebooks = notebooks
        self.folders = folders

        # Reference towards the currently edited/previewed notebook
        self.current_notebook = ''
        # Stores the SHA sum for every notebook, in order to avoid re-analyzing
        # the entire file for each filtering TODO
        self.sha = {}

        # get saved settings
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")

        # Switch that holds the property to either display or hide empty
        # folders in the shelves
        if self.settings.contains("display_empty"):
            if self.settings.value("display_empty") == "true":
                self.display_empty = True
            else:
                self.display_empty = False
        else:
            self.display_empty = True
        
