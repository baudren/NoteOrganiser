from PySide import QtGui
from PySide import QtCore
# Frame to test
import pytest
from ..NoteOrganiser import NoteOrganiser


def test_initialisation(qtbot, mock):
    # Specifying a different folder for storing everything (for testing
    # purposes)
    dialog = QtGui.QFileDialog()
    dialog.setFileMode(QtGui.QFileDialog.Directory)
    dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
    qtbot.addWidget(dialog)
    def cancel_dialog():
        qtbot.click(dialog.cancel)

    QtCore.QTimer.singleShot(200, cancel_dialog)
    note = NoteOrganiser()
    # Creating a NoteOrganiser and adding it to the bot
    qtbot.addWidget(note)

