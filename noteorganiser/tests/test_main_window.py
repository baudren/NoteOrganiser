import os
from PySide import QtGui
from PySide import QtCore
# Frame to test
import pytest
from ..NoteOrganiser import NoteOrganiser


def test_initialisation(qtbot, mocker):
    # Specifying a different folder for storing everything (for testing
    # purposes)
    #dialog = QtGui.QFileDialog()
    #dialog.setFileMode(QtGui.QFileDialog.Directory)
    #dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    #qtbot.addWidget(dialog)
    #def cancel_dialog():
        #qtbot.click(dialog.cancel)

    home = os.path.expanduser("~")
    #QtCore.QTimer.singleShot(200, cancel_dialog)
    main = os.path.join(home, '.noteorganiser')
    print main
    mocker.patch.object(
        QtGui.QFileDialog, 'getExistingDirectory',
        return_value=main)
    note = NoteOrganiser()
    # Creating a NoteOrganiser and adding it to the bot
    qtbot.addWidget(note)

