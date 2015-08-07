import os
import importlib
from robot.api import logger

from PySide import QtGui
from PySide import QtTest

from keywords import ConfigurationKeywords, LibraryKeywords
from PysideLibrary import PysideLibrary

class NoteOrganiserTesting (PysideLibrary, ConfigurationKeywords, LibraryKeywords):


    def open_note_organiser(self, *args, **kwargs):
        module = 'noteorganiser.NoteOrganiser'
        name = 'NoteOrganiser'
        PysideLibrary.open_application(self, module, name, *args, **kwargs)

    def close_note_organiser(self):
        self.close_application()

    def clean_all_stored_settings(self):
        raise NotImplementedError

    def folder_choice_should_be_present(self):
        raise NotImplementedError

    def pick_a_storage_folder_for_the_first_time(self):
        raise NotImplementedError
        return ''

    def get_storage_folder(self):
        raise NotImplementedError
        return ''
