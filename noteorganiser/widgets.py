from __future__ import unicode_literals
import sys

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
            painter.translate(42, 90)
            painter.rotate(-90)
        elif self.style == 'folder':
            painter.translate(20, 110)
        painter.setFont(QtGui.QFont('unicode', 12))
        painter.drawText(event.rect(), self.text)

    def sizeHint(self):
        return self.pixmap.size()

    def mouseReleaseEvent(self, ev):
        """Define a behaviour under click"""
        self.click()

    def removeButton(self):
        """Delegate to the parent to deal with the situation"""
        self.deleteNotebook.emit(self.text)


if __name__ == "__main__":
    # Testing the clickable buttons with picture
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(window)

    button = PicButton(QtGui.QPixmap(
        "./noteorganiser/assets/notebook-128.png"), 'something', 'notebook')
    layout.addWidget(button)

    window.show()
    sys.exit(app.exec_())
