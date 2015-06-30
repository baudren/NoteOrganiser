import os
from PySide import QtGui
from PySide import QtCore
# Frame to test
import pytest
from ..NoteOrganiser import NoteOrganiser


def test_initialisation(qtbot, mocker):
    # Specifying a different folder for storing everything (for testing
    # purposes)
    home = os.path.expanduser("~")
    main = os.path.join(home, '.noteorganiser')
    mocker.patch.object(
        QtGui.QFileDialog, 'getExistingDirectory',
        return_value=main)
    note = NoteOrganiser()
    # Creating a NoteOrganiser and adding it to the bot
    qtbot.addWidget(note)

