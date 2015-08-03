from __future__ import unicode_literals

import re
import os
from PySide import QtGui
from PySide import QtCore

os.environ['QT_API'] = 'PySide'
import qtawesome

from .utils import MultiCompleter


class PicButton(QtGui.QPushButton):
    """Button with a picture"""
    deleteNotebookSignal = QtCore.Signal(str)
    deleteFolderSignal = QtCore.Signal(str)
    previewSignal = QtCore.Signal(str)

    def __init__(self, pixmap, text, style, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.parent = parent
        self.label = str(text)
        # Define the tooltip
        self.setToolTip(self.label)
        self.pixmap = pixmap
        self.style = style

        # Default fontsize
        self.default = 9
        self.fontsize = self.default

        # Define behaviour under right click
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        delete = QtGui.QAction(self)
        delete.setText("delete")
        delete.triggered.connect(self.removeButton)
        self.addAction(delete)

        # use the preview action only on notebook
        if self.style == 'notebook':
            # Define behaviour for direct preview
            preview = QtGui.QAction(self)
            preview.setText("preview")
            preview.triggered.connect(self.previewNotebook)
            self.addAction(preview)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setFont(QtGui.QFont('unicode', self.fontsize))

        # If the width of the text is too large, reduce the fontsize
        metrics = QtGui.QFontMetrics(self.font())
        if metrics.width(self.label) > 76:
            self.fontsize = 7
            painter.setFont(QtGui.QFont('unicode', self.fontsize))

        # If the width is still too large, elide the text
        elided = metrics.elidedText(
            self.label, QtCore.Qt.ElideRight, 90)

        painter.drawPixmap(event.rect(), self.pixmap)
        if self.style == 'notebook':
            painter.translate(42, 102)
            painter.rotate(-90)
        elif self.style == 'folder':
            painter.translate(10, 100+self.default-self.fontsize)
        painter.drawText(event.rect(), elided)

    def sizeHint(self):
        return self.pixmap.size()

    def mouseReleaseEvent(self, ev):
        """Define a behaviour under click"""
        # only fire event, when left button is clicked
        if ev.button() == QtCore.Qt.LeftButton:
            # check for shift-key
            modifiers = QtGui.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                self.previewNotebook()
            else:
                self.click()

    def removeButton(self):
        """Delegate to the parent to deal with the situation"""
        if self.style == 'notebook':
            self.deleteNotebookSignal.emit(self.label)
        else:
            self.deleteFolderSignal.emit(self.label)

    def previewNotebook(self):
        """emmit signal to preview the current notebook"""
        self.previewSignal.emit(self.label)


class VerticalScrollArea(QtGui.QScrollArea):
    """Implementation of a purely vertical scroll area"""

    def __init__(self, parent=None):
        QtGui.QScrollArea.__init__(self, parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().setFocusPolicy(QtCore.Qt.StrongFocus)

    def eventFilter(self, item, event):
        """
        This works because setWidget installs an eventFilter on the widget"""
        if (item and item == self.widget()
                and event.type() == QtCore.QEvent.Resize):
            self.setMinimumWidth(
                self.widget().minimumSizeHint().width() +
                self.verticalScrollBar().width())
        return QtGui.QScrollArea.eventFilter(self, item, event)


class LineEditWithClearButton(QtGui.QLineEdit):
    """a line edit widget that shows a clear button if there is text"""
    buttonClicked = QtCore.Signal(bool)

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)

        self.clearButton = QtGui.QPushButton('x', self)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.red)
        self.clearButton.setPalette(palette)
        self.clearButton.setStyleSheet('border: 0px;'
                                       'padding: 0px;'
                                       'padding-right: 3px;'
                                       'font-weight: bold;')
        self.clearButton.setCursor(QtCore.Qt.ArrowCursor)
        self.clearButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clearButton.setVisible(False)
        self.clearButton.clicked.connect(self.clear)
        self.textChanged.connect(self.showClearButton)

        frameWidth = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.clearButton.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' %
                           (buttonSize.width() + frameWidth))
        self.setMinimumSize(max(self.minimumSizeHint().width(),
                            buttonSize.width() + frameWidth*2),
                            max(self.minimumSizeHint().height(),
                                buttonSize.height() + frameWidth*2))

    def resizeEvent(self, event):
        """move the clear button with the widget"""
        buttonSize = self.clearButton.sizeHint()
        frameWidth = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        self.clearButton.move(self.rect().right() - frameWidth -
                              buttonSize.width(), (self.rect().bottom() -
                              buttonSize.height() + 1)/2)
        QtGui.QLineEdit.resizeEvent(self, event)

    def showClearButton(self):
        """show the clear button if there's text"""
        self.clearButton.setVisible(len(self.text()))


class TagCompletion(QtGui.QLineEdit):
    """ a QLineEdit with a QCompleter to add tags from the current file """

    def __init__(self, tags, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.parent = parent
        self.initTagCompletion(tags)
        self.initCompleteButton()

    def initTagCompletion(self, tags=None):
        """add a multi-item completer to the given widget"""
        if tags is None:
            tags = []

        tags = sorted(tags)
        self.completer = MultiCompleter(list(tags), self)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(self.completer)
        self.returnPressed.connect(self.onReturnPressed)

    def initCompleteButton(self):
        """add a little down-arrow to start completion
        (list all available tags)"""
        completeIcon = qtawesome.icon('fa.sort-down')
        self.completeButton = QtGui.QPushButton(completeIcon, '', self)
        self.completeButton.setStyleSheet('border: 0px;'
                                          'padding: 0px;')
        self.completeButton.setCursor(QtCore.Qt.ArrowCursor)
        self.completeButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.completeButton.clicked.connect(self.onCompletePressed)
        frameWidth = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.completeButton.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' %
                           (buttonSize.width() + frameWidth))
        self.setMinimumSize(max(self.minimumSizeHint().width(),
                            buttonSize.width() + frameWidth*2),
                            max(self.minimumSizeHint().height(),
                                buttonSize.height() + frameWidth*2))

    def resizeEvent(self, event):
        """move the clear button with the widget"""
        buttonSize = self.completeButton.sizeHint()
        frameWidth = self.style().pixelMetric(
            QtGui.QStyle.PM_DefaultFrameWidth)
        self.completeButton.move(self.rect().right() - frameWidth -
                                 buttonSize.width(), (self.rect().bottom() -
                                 buttonSize.height() + 1)/2)
        QtGui.QLineEdit.resizeEvent(self, event)

    def onReturnPressed(self):
        """ get the first item from the completer """

        self.completer.setCompletionPrefix(self.text())
        if self.completer.completionModel().rowCount():
            self.setText(self.completer.currentCompletion())

    def onCompletePressed(self):
        """Complete Button was pressed: start completion"""
        self.completer.setCompletionPrefix(self.text())
        self.completer.complete()

    def getTextWithNormalizedSeparators(self):
        """
        get the text with all separators replaced by separators[0]

        separators[0] is normally ','.
        This corresponds to the separator used for tags in the markdown files
        """

        return re.sub(r'[{0}]'.format(''.join(self.completer.separators)),
                      self.completer.separators[0], self.text())
