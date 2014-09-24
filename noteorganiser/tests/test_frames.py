import os
import sys
import shutil
import datetime
from PySide import QtGui
from PySide import QtCore
import pytest

from ..frames import Shelves, TextEditor
from ..widgets import PicButton
from ..logger import create_logger
from ..configuration import search_folder_recursively
from ..constants import EXTENSION
from .. import configuration as conf


@pytest.fixture
def parent(request, qtbot):
    date = str(datetime.date.today())
    home = os.path.join(os.path.expanduser("~"), '.noteorganiser')
    # Create the temp folder
    temp_folder_path = os.path.join(
        home, '.test_%s' % date)
    if not os.path.isdir(temp_folder_path):
        os.mkdir(temp_folder_path)
    # Copy there the example.md file, create a subfolder, and put again the
    # same example.md in the subfolder
    shutil.copy(
        os.path.join(os.path.os.getcwd(), 'example', 'example.md'),
        temp_folder_path)
    subfolder = os.path.join(temp_folder_path, 'toto')
    os.mkdir(subfolder)
    shutil.copy(
        os.path.join(os.path.os.getcwd(), 'example', 'example.md'),
        subfolder)
    # Create a parent window, containing an information instance, and a
    # logger
    parent = QtGui.QFrame()
    qtbot.addWidget(parent)
    log = create_logger('CRITICAL', 'stream')
    # Create an info instance
    # Search the folder recursively
    notebooks, folders = search_folder_recursively(log, temp_folder_path)
    info = conf.Information(log, temp_folder_path, notebooks, folders)
    parent.info = info
    parent.log = log

    def fin():
        """Tear down parent class"""
        shutil.rmtree(temp_folder_path)
        parent.destroy()
    request.addfinalizer(fin)

    return parent


def test_shelves(qtbot, parent, mock):
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

    # Test right click on the notebook. It should not trigger a switch tab
    with qtbot.waitSignal(shelves.refreshSignal, timeout=100) as right:
        qtbot.mouseClick(shelves.buttons[0], QtCore.Qt.RightButton)
    assert not right.signal_triggered

    # Test right click, should open the menu TODO
    # Test clicking on the menu, should actually delete the file, and send a
    # refresh signal. TODO. temporary fix: call directly removeNotebook method
    with qtbot.waitSignal(shelves.refreshSignal, timeout=1000) as remove:
        # Mock the question QMessageBox
        mock.patch.object(QtGui.QMessageBox, 'question',
                          return_value=QtGui.QMessageBox.No)
        shelves.removeNotebook('example')
        # Check nothing happened
        assert len(shelves.buttons) == 2, \
            "Saying no to the question did not stop the removal"
        mock.patch.object(QtGui.QMessageBox, 'question',
                          return_value=QtGui.QMessageBox.Yes)
        shelves.removeNotebook('example')
    assert remove.signal_triggered

    # Check now that the buttons attribute only contains the folder
    assert len(shelves.buttons) == 1, \
        "the notebook was not removed from the shelves"
    assert not shelves.info.notebooks, \
        "the notebook was not removed from the information instance"

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

        assert len(shelves.buttons) == 2, "the notebook was not created"
        assert shelves.info.notebooks == ['toto'+EXTENSION], \
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
    assert text_editor.text.toPlainText().encode('utf-8') is not None, \
        "The source file was not read"

    def check_final_line(text, check_new_line=True):
        if check_new_line:
            start = -len(text)-1
            new_text = text_editor.text.toPlainText().encode('utf-8')[start:]
            control = "\n"+text
        else:
            start = -len(text)
            new_text = text_editor.text.toPlainText().encode('utf-8')[start:]
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
