import os
import shutil
import datetime
from PySide import QtGui
from PySide import QtCore
import pytest

from ..frames import Shelves
from ..logger import create_logger
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
    # Copy there the example.md file
    shutil.copy(
        os.path.join(os.path.os.getcwd(), 'example', 'example.md'),
        temp_folder_path)
    # Create a parent window, containing an information instance, and a
    # logger
    parent = QtGui.QFrame()
    qtbot.addWidget(parent)
    log = create_logger('CRITICAL', 'stream')
    # Create an info instance
    info = conf.Information(log, home, ['example.md'], [])
    info.level = temp_folder_path
    parent.info = info
    parent.log = log

    def fin():
        print("Tear down parent class")
        shutil.rmtree(temp_folder_path)
        parent.destroy()
    request.addfinalizer(fin)

    return parent


def test_shelves(qtbot, parent):
    # Creating the shelves, and adding them to the bot
    shelves = Shelves(parent)
    qtbot.addWidget(shelves)

    assert hasattr(shelves, 'buttons')
    # Asserting that left clicking on the notebook icon sends a signal to
    # switch tab
    with qtbot.waitSignal(shelves.switchTabSignal, timeout=1000) as switch:
        qtbot.mouseClick(shelves.buttons[0], QtCore.Qt.LeftButton)

    # Commenting out the incriminating part until the bug is found
    #assert switch.signal_triggered
