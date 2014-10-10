import os
import shutil
import datetime
from PySide import QtGui
from PySide import QtCore
import pytest

# Frames to test
from ..frames import Shelves
from ..frames import TextEditor
from ..frames import Editing
from .custom_fixtures import parent

from ..widgets import PicButton
from ..constants import EXTENSION

def test_shelves_remove_cancel(qtbot, parent, mocker):
    # Creating the shelves, and adding them to the bot
    shelves = Shelves(parent)
    qtbot.addWidget(shelves)

    # Test right click, should open the menu TODO
    # Test clicking on the menu, should actually delete the file, and send a
    # refresh signal. TODO. temporary fix: call directly removeNotebook method
    # Mock the question QMessageBox
    mocker.patch.object(QtGui.QMessageBox, 'question', autospect=True,
                        return_value=QtGui.QMessageBox.No)
    shelves.removeNotebook('example')
    # Check that nothing happened
    assert len(shelves.buttons) == 2, \
        "Saying no to the question did not stop the removal"


def test_shelves_remove_accept(qtbot, parent, mocker):
    # Creating the shelves, and adding them to the bot
    shelves = Shelves(parent)
    qtbot.addWidget(shelves)

    with qtbot.waitSignal(shelves.refreshSignal, timeout=2000) as remove:
        mocker.patch.object(QtGui.QMessageBox, 'question', autospect=True,
                            return_value=QtGui.QMessageBox.Yes)
        shelves.removeNotebook('example')
    assert remove.signal_triggered
    # Check that the file was indeed removed
    assert len(shelves.buttons) == 1, \
        "Saying yes to the question did not remove the notebook"



def test_shelves(qtbot, parent, mocker):
    # Creating the shelves, and adding them to the bot
    shelves = Shelves(parent)
    qtbot.addWidget(shelves)

    # Checking if the buttons list was created, and that it contains only two
    # elements (the notebook, and the folder)
    assert hasattr(shelves, 'buttons'), 'buttons attribute not created'
    assert len(shelves.buttons) == 2, 'not all buttons were created'
    for button in shelves.buttons:
        assert isinstance(button, PicButton)
    # Asserting that left clicking on the notebook icon (first element of the
    # buttons attribute) sends the proper signal.
    with qtbot.waitSignal(shelves.switchTabSignal, timeout=1000) as switch:
        qtbot.mouseClick(shelves.buttons[0], QtCore.Qt.LeftButton)
    assert switch.signal_triggered, \
        "clicking on a notebook should trigger a switchTabSignal"

    # Checking that the up button is currently inaccessible (we are still in
    # the root folder
    assert not shelves.upButton.isEnabled(), \
        "upButton should be disabled while in root"

    # Checking the behaviour when clicking on a folder
    with qtbot.waitSignal(shelves.refreshSignal, timeout=1000) as way_down:
        qtbot.mouseClick(shelves.buttons[1], QtCore.Qt.LeftButton)
        # Check that the info.level has changed properly
        assert shelves.info.level != shelves.info.root, "did not change dir"
        # Check that now, the upButton is enabled
        assert shelves.upButton.isEnabled(), "upButton was not enabled"
    assert way_down.signal_triggered, "going down did not send a refreshSignal"

    # Go back to the root
    with qtbot.waitSignal(shelves.refreshSignal, timeout=1000) as way_up:
        qtbot.mouseClick(shelves.upButton, QtCore.Qt.LeftButton)
        assert shelves.info.level == shelves.info.root, \
            "the upButton did not go back up"
        assert not shelves.upButton.isEnabled(), \
            "the upButton was not properly reconnected"
    assert way_up.signal_triggered, "going up did not send a refreshSignal"

    # Test right click on the notebook. It should **not** trigger a switch tab
    with qtbot.waitSignal(shelves.refreshSignal, timeout=100) as right:
        qtbot.mouseClick(shelves.buttons[0], QtCore.Qt.RightButton)
    assert not right.signal_triggered

    # Adding a notebook
    def interact_newN():
        # Create a notebook called toto
        qtbot.keyClicks(shelves.popup.nameLineEdit, 'toto')
        qtbot.mouseClick(shelves.popup.createButton, QtCore.Qt.LeftButton)

    with qtbot.waitSignal(shelves.refreshSignal, timeout=2000) as newN:
        # Create a timer, to let the window be created, then fill in the
        # information
        QtCore.QTimer.singleShot(200, interact_newN)
        qtbot.mouseClick(shelves.newNotebookButton, QtCore.Qt.LeftButton)

        assert len(shelves.buttons) == 3, "the notebook was not created"
        assert shelves.info.notebooks[-1] == 'toto'+EXTENSION, \
            "the notebook was not added to the information instance"
    assert newN.signal_triggered

    # Adding a folder
    def interact_newF():
        qtbot.keyClicks(shelves.popup.nameLineEdit, 'titi')
        qtbot.mouseClick(shelves.popup.createButton, QtCore.Qt.LeftButton)

    with qtbot.waitSignal(shelves.refreshSignal, timeout=1000) as newF:
        QtCore.QTimer.singleShot(200, interact_newF)
        qtbot.mouseClick(shelves.newFolderButton, QtCore.Qt.LeftButton)
        assert len(shelves.buttons) == 0, \
            "the folder was not created, or the level was not changed"
        # Create a notebook called toto inside the titi folder
        QtCore.QTimer.singleShot(200, interact_newN)
        qtbot.mouseClick(shelves.newNotebookButton, QtCore.Qt.LeftButton)

        assert len(shelves.buttons) == 1, "the notebook was not created"
        assert shelves.info.notebooks == ['toto'+EXTENSION], \
            "the notebook was not added to the information instance"

    assert newF.signal_triggered


def test_text_editor(qtbot, parent):
    text_editor = TextEditor(parent)
    qtbot.addWidget(text_editor)

    # Load the file
    source = os.path.join(parent.info.level, parent.info.notebooks[0])
    text_editor.setSource(source)

    # check that now the text is non-empty
    assert text_editor.text.toPlainText() is not None, \
        "The source file was not read"

    def check_final_line(text, check_new_line=True):
        if check_new_line:
            start = -len(text)-1
            new_text = text_editor.text.toPlainText()[start:]
            control = "\n"+text
        else:
            start = -len(text)
            new_text = text_editor.text.toPlainText()[start:]
            control = text
        assert new_text == control, "The line was not added properly"

    # append a line with the method appendText used in NewEntry
    text_editor.appendText("Life is beautiful")
    check_final_line("Life is beautiful")

    # Check that it has been saved while appending by reloading
    text_editor.setSource(source)
    check_final_line("Life is beautiful")

    # Try to write in the end without saving, and reloading
    # TODO how to input a "enter" pressed, ie, carriage return?
    qtbot.keyClicks(text_editor.text, 'Life is beautiful')
    check_final_line("Life is beautiful", check_new_line=False)

    # Reload from disk, and check that the last line is gone (i.e., that there
    # is still the "\nLife is beautiful", and not "\nLife is BeautifulLife is
    # beautiful"
    qtbot.mouseClick(text_editor.readButton, QtCore.Qt.LeftButton)
    check_final_line("Life is beautiful")

    # Try to zoom out, in, and reset, simply testing that the font has been
    # updated, the text has the proper font, and that the pointSize has the
    # right value
    def check_font_size(size):
        font = text_editor.font
        text_font = text_editor.text.font()
        # Check that the font was set to the right value
        assert font.pointSize() == size
        # Check that the text was properly updated
        assert font.pointSize() == text_font.pointSize()

    text_editor.zoomIn()
    check_font_size(text_editor.defaultFontSize+1)

    text_editor.zoomOut()
    text_editor.zoomOut()
    check_font_size(text_editor.defaultFontSize-1)

    text_editor.resetSize()
    check_font_size(text_editor.defaultFontSize)


def test_editing(qtbot, parent):
    """Test the editing tab"""
    editing = Editing(parent)
    qtbot.addWidget(editing)

    # Check that there is only one tab
    assert editing.tabs.count() == 1, "the tabs were not created properly"

    # Test the new entry button
    def interact_newEntry():
        # Create a post called toto, with tags tata and tutu and entry titi
        qtbot.keyClicks(editing.popup.titleLineEdit, 'toto')
        qtbot.keyClicks(editing.popup.tagsLineEdit, 'tata, tutu')
        qtbot.keyClicks(editing.popup.corpusBox, 'titi')
        qtbot.mouseClick(editing.popup.okButton, QtCore.Qt.LeftButton)

    QtCore.QTimer.singleShot(200, interact_newEntry)
    qtbot.mouseClick(editing.newEntryButton, QtCore.Qt.LeftButton)

    # Check that the entry was appended, with the date properly set
    new_text = editing.tabs.currentWidget().text.toPlainText()[
        -44:]
    expectation = '\ntoto\n----\n# tata, tutu\n\n*%s*\n\ntiti\n' % (
        datetime.date.today().strftime("%d/%m/%Y"))
    assert new_text == expectation, "The new entry was not appended %s, %s" % (
        new_text, expectation)

    # Check if preview button works by sending the signal loadNotebook
    with qtbot.waitSignal(editing.loadNotebook, timeout=1000) as preview:
        qtbot.mouseClick(editing.previewButton, QtCore.Qt.LeftButton)

    assert preview.signal_triggered, \
        "asking for previewing does not send the right signal"
