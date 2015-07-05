import os
import shutil
import datetime
from qtpy import QtGui
from qtpy import QtCore
from qtpy import QtWidgets
import pytest

# Frames to test
from ..frames import CustomFrame
from ..frames import Library
from ..frames import Shelves
from ..frames import TextEditor
from ..frames import Editing
from ..frames import Preview
from .custom_fixtures import parent

from ..widgets import PicButton
from ..constants import EXTENSION


def test_custom_frame(qtbot, parent):
    # Creating a basic frame. This should raise a NotImplementedError
    with pytest.raises(NotImplementedError):
        CustomFrame(parent)

    # Define a daughter class which implements a dummy initUI method. Then,
    # calling zoomIn, zoomOut or resetSize should also raise a
    # NotImplementedError
    class Dummy(CustomFrame):
        def initUI(self):
            pass

    dummy = Dummy(parent)
    qtbot.addWidget(dummy)
    with pytest.raises(NotImplementedError):
        dummy.zoomIn()
    with pytest.raises(NotImplementedError):
        dummy.zoomOut()
    with pytest.raises(NotImplementedError):
        dummy.resetSize()


def test_library(qtbot, parent):
    # Creating the object and adding it to the bot
    library = Library(parent)
    qtbot.addWidget(library)

    # Check the nature of the shelves object
    assert hasattr(library, 'shelves')
    assert isinstance(library.shelves, Shelves)

    # Check that the refresh method of the library at least call the refresh
    # method of the shelves, and therefore, emits the expected signal
    with qtbot.waitSignal(library.shelves.refreshSignal, timeout=1000) as \
            refresh:
        library.refresh()
    assert refresh.signal_triggered, \
        "refreshing the library should transmit the signal to the shelves"


def test_shelves(qtbot, parent, mocker):
    # Creating the shelves, and adding them to the bot
    shelves = Shelves(parent)
    qtbot.addWidget(shelves)

    # Checking if the buttons list was created, and that it contains only two
    # elements (the notebook, and the folder)
    assert hasattr(shelves, 'buttons'), 'buttons attribute not created'
    assert len(shelves.buttons) == 3, 'not all buttons were created'
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
        qtbot.mouseClick(shelves.buttons[2], QtCore.Qt.LeftButton)
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

    # Test right click, should open the menu TODO
    # Test clicking on the menu, should actually delete the file, and send a
    # refresh signal. TODO. temporary fix: call directly removeNotebook method
    # Mock the question QMessageBox
    question = mocker.patch.object(QtWidgets.QMessageBox, 'question',
                                   return_value=QtWidgets.QMessageBox.No)
    shelves.removeNotebook('example')
    # Check that nothing happened
    assert len(shelves.buttons) == 3, \
        "Saying no to the question did not stop the removal"

    with qtbot.waitSignal(shelves.refreshSignal, timeout=2000) as remove:
        # Reuse the question object because of a Pyside bug under Python 3.3
        question.return_value = QtWidgets.QMessageBox.Yes
        shelves.removeNotebook('example')
    assert remove.signal_triggered
    # Check that the file was indeed removed
    assert len(shelves.buttons) == 2, \
        "Saying yes to the question did not remove the notebook"

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

    # Go back, and check that creating a new folder that already exists does
    # not overwrite it
    qtbot.mouseClick(shelves.upButton, QtCore.Qt.LeftButton)

    def interact_existingF():
        qtbot.keyClicks(shelves.popup.nameLineEdit, 'toto')
        qtbot.mouseClick(shelves.popup.createButton, QtCore.Qt.LeftButton)

    with qtbot.waitSignal(shelves.refreshSignal, timeout=1000) as existingF:
        QtCore.QTimer.singleShot(200, interact_existingF)
        qtbot.mouseClick(shelves.newFolderButton, QtCore.Qt.LeftButton)
        assert len(shelves.buttons) == 1, \
            "the existing folder was overwritten"
    assert existingF.signal_triggered

    # Create an empty file, and remove it TODO

    # test preview function on shift click
    # this should show the clicked notebook in the preview-tab
    new_index = 0
    with qtbot.waitSignal(shelves.refreshSignal, timeout=100) as right:
        with qtbot.waitSignal(shelves.previewSignal, timeout=1000) as switch:
            qtbot.mouseClick(shelves.buttons[new_index], QtCore.Qt.LeftButton,
                             QtCore.Qt.ShiftModifier)
        assert switch.signal_triggered, \
            "shift-clicking on a notebook should trigger a previewSignal"
    assert not right.signal_triggered, \
        "shift-clicking should NOT trigger a refreshSignal"


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
    assert editing.tabs.count() == 2, "the tabs were not created properly"

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

    # Test the tabs (should switch from one notebook to the other)
    # Check that there are two of them
    assert editing.tabs.count() == 2

    initial_index = editing.tabs.currentIndex()
    new_index = initial_index % 2
    new_notebook = editing.info.notebooks[new_index]
    editing.switchNotebook(new_notebook[:-3])
    assert editing.tabs.currentIndex() == new_index
    # Test the refresh method by removing directly on the disk a file

    os.remove(
        os.path.join(editing.info.root, 'second'+EXTENSION))
    editing.info.notebooks.pop(
        editing.info.notebooks.index('second'+EXTENSION))
    editing.refresh()
    # There should be only one tab left
    assert editing.tabs.count() == 1

    # Check that zoom-in, zoom-out, reset size are implemented
    editor = editing.tabs.currentWidget()

    # Fontsize should be bigger
    editing.zoomIn()
    assert editor.text.currentFont().pointSize() > editor.defaultFontSize

    # Zoom out twice should get the Point size smaller
    editing.zoomOut()
    editing.zoomOut()
    assert editor.text.currentFont().pointSize() < editor.defaultFontSize

    # Reset should reset it...
    editing.resetSize()
    assert editor.text.currentFont().pointSize() == editor.defaultFontSize


def test_preview(qtbot, parent):
    preview = Preview(parent)
    qtbot.addWidget(preview)

    # Load a notebook
    preview.loadNotebook(preview.info.notebooks[0])

    # assert tagButtons contains six elements
    assert len(preview.tagButtons) == 6
    assert isinstance(preview.tagButtons[0][1], QtWidgets.QPushButton)

    # Click on the first tag button
    first_key, first_button = preview.tagButtons[0]
    qtbot.mouseClick(first_button, QtCore.Qt.LeftButton)

    assert len(preview.filters) == 1
    assert preview.filters[0] == first_key

    # Click on another, disabled button
    for key, button in preview.tagButtons:
        if key not in preview.remaining_tags:
            qtbot.mouseClick(button, QtCore.Qt.LeftButton)
            assert len(preview.filters) == 1

    # Add another filter
    for key, button in preview.tagButtons:
        if key in preview.remaining_tags and key != first_key:
            newFilter = [key, button]
            break

    qtbot.mouseClick(newFilter[1], QtCore.Qt.LeftButton)
    assert len(preview.filters) == 2

    # Unclick both
    qtbot.mouseClick(newFilter[1], QtCore.Qt.LeftButton)
    qtbot.mouseClick(first_button, QtCore.Qt.LeftButton)

    # Test zoom
    preview.zoomIn()
    preview.zoomOut()
    preview.resetSize()

    # Reload should work (how to test that it truly works?)
    preview.reload()
