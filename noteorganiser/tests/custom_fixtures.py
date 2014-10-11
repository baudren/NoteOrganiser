import os
import shutil
import datetime
import pytest
from PySide import QtGui

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
