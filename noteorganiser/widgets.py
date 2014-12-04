from __future__ import unicode_literals

from PySide import QtGui
from PySide import QtCore


class PicButton(QtGui.QPushButton):
    """Button with a picture"""
    deleteNotebook = QtCore.Signal(str)

    def __init__(self, pixmap, text, style, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.parent = parent
        self.text = str(text)
        self.pixmap = pixmap
        self.style = style

        # Define behaviour under right click
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        delete = QtGui.QAction(self)
        delete.setText("delete")
        delete.triggered.connect(self.removeButton)
        self.addAction(delete)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)
        if self.style == 'notebook':
            painter.translate(42, 102)
            painter.rotate(-90)
        elif self.style == 'folder':
            painter.translate(10, 110)
        if len(self.text) > 10:
            fontsize = 9
        else:
            fontsize = 12
        painter.setFont(QtGui.QFont('unicode', fontsize))
        painter.drawText(event.rect(), self.text)

    def sizeHint(self):
        return self.pixmap.size()

    def mouseReleaseEvent(self, ev):
        """Define a behaviour under click"""
        # only fire event, when left button is clicked
        if ev.button() == QtCore.Qt.LeftButton:
            self.click()

    def removeButton(self):
        """Delegate to the parent to deal with the situation"""
        self.deleteNotebook.emit(self.text)


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
