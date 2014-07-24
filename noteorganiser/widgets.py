import sys
from PySide import QtGui


class Shelves(QtGui.QWidget):

    def __init__(self, notebook_list):
        QtGui.QWidget.__init__(self)

        self.notebook_list = notebook_list
        self.initUI()

    def initUI(self):
        """Create the physical shelves"""

        grid = QtGui.QGridLayout()
        grid.setSpacing(100)

        notebooks = []
        for index, notebook in enumerate(self.notebook_list):
            button = PicButton(QtGui.QPixmap(
                "./noteorganiser/assets/notebook-128.png"))
            button.setMinimumSize(128, 128)
            button.setMaximumSize(128, 128)
            notebooks.append(button)
            grid.addWidget(button, 0, index)

        self.setLayout(grid)


class PicButton(QtGui.QAbstractButton):
    def __init__(self, pixmap, parent=None):
        QtGui.QAbstractButton.__init__(self, parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(window)

    button = PicButton(QtGui.QPixmap(
        "./noteorganiser/assets/notebook-128.png"))
    layout.addWidget(button)

    window.show()
    sys.exit(app.exec_())
