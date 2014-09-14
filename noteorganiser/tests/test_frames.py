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


def test_shelves(qtbot, parent):
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
        shelves.removeNotebook('example')
        # So far, it is needed to manually click on the popup window: this
        # should not be the case.
        #qtbot.mouseClick(shelves.reply.Ok, QtCore.Qt.LeftButton)
    assert remove.signal_triggered

    # Check now that the buttons attribute only contains the folder
    assert len(shelves.buttons) == 1, \
        "the notebook was not removed from the shelves"
    assert not shelves.info.notebooks, \
        "the notebook was not removed from the information instance"


def test_text_editor(qtbot, parent):
    text_editor = TextEditor(parent)
    qtbot.addWidget(text_editor)

    # modify text, save it, reload it, assert it has been changed, etc..
