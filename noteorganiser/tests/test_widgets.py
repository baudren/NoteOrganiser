"""tests for custom widgets"""
from PySide import QtGui
from PySide import QtCore

#widgets to test
from ..widgets import LineEditWithClearButton
from .custom_fixtures import parent


def test_LineEditWithClearButton(qtbot, parent):
    lineEdit = LineEditWithClearButton()
    qtbot.addWidget(lineEdit)

    assert hasattr(lineEdit, 'clearButton')

    assert not len(lineEdit.text())
    assert not lineEdit.clearButton.isVisibleTo(lineEdit)
    qtbot.keyClicks(lineEdit, 'titi')
    assert len(lineEdit.text())
    assert lineEdit.clearButton.isVisibleTo(lineEdit)
    qtbot.mouseClick(lineEdit.clearButton, QtCore.Qt.LeftButton)
    assert not len(lineEdit.text())
    assert not lineEdit.clearButton.isVisibleTo(lineEdit)
