"""tests for custom widgets"""

from PySide import QtGui
from PySide import QtCore

#widgets to test
from ..widgets import LineEditWithClearButton
from ..widgets import TagCompletion
from ..utils import MultiCompleter
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


def test_TagCompletion(qtbot, parent):
    tags = ['toto', 'tata']
    tagCompletion = TagCompletion(tags)
    qtbot.addWidget(tagCompletion)

    # check that our Completer is our own MultiCompleter
    assert isinstance(tagCompletion.completer, MultiCompleter)

    # check filtering
    qtbot.keyClicks(tagCompletion, 't')
    assert tagCompletion.completer.completionModel().rowCount() == 2
    qtbot.keyClicks(tagCompletion, 'a')
    assert tagCompletion.completer.completionModel().rowCount() == 1
    qtbot.keyClicks(tagCompletion, 'x')
    assert tagCompletion.completer.completionModel().rowCount() == 0

    tagCompletion.clear()
    assert tagCompletion.text() == ''

    # check completion
    qtbot.keyClicks(tagCompletion, 't')
    qtbot.keyPress(tagCompletion, QtCore.Qt.Key_Enter)
    assert tagCompletion.text() == ' tata'

    # check second completion after separator
    qtbot.keyClicks(tagCompletion, ', to')
    qtbot.keyPress(tagCompletion, QtCore.Qt.Key_Enter)
    assert tagCompletion.text() == ' tata, toto'

    # check other separator
    qtbot.keyClicks(tagCompletion, '; ta')
    qtbot.keyPress(tagCompletion, QtCore.Qt.Key_Enter)
    assert tagCompletion.text() == ' tata, toto; tata'

    # check that another press on Return doesn't change the text
    qtbot.keyPress(tagCompletion, QtCore.Qt.Key_Enter)
    assert tagCompletion.text() == ' tata, toto; tata'

    # check the down button
    assert not tagCompletion.completer.popup().isVisible()
    qtbot.mouseClick(tagCompletion.downButton, QtCore.Qt.LeftButton)
    assert tagCompletion.completer.popup().isVisible()

    # check normalization of separators
    assert tagCompletion.getTextWithNormalizedSeparators() == \
        ' tata, toto, tata'

    # check switching of separators
    tagCompletion.completer.setSeparators([';', ','])
    assert tagCompletion.completer.separators == [';', ',']
    assert tagCompletion.getTextWithNormalizedSeparators() == \
        ' tata; toto; tata'
