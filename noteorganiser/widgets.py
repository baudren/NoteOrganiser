from __future__ import unicode_literals

from PySide import QtGui
from PySide import QtCore


class PicButton(QtGui.QPushButton):
    """Button with a picture"""
    deleteNotebook = QtCore.Signal(str)

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
            self.click()

    def removeButton(self):
        """Delegate to the parent to deal with the situation"""
        self.deleteNotebook.emit(self.label)


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
