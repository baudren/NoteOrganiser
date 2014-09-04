import sys
import os

from PySide import QtGui
from PySide import QtCore

from constants import EXTENSION
from configuration import search_folder_recursively


class Shelves(QtGui.QFrame):

    def __init__(self, notebooks, folders, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.parent = parent
        self.notebooks = notebooks
        self.folders = folders
        self.setLayout(QtGui.QVBoxLayout())
        self.initUI()

        # Store the level of exploration (the current folder). Initially, it is
        # the root folder
        self.level = self.parent.parent.root

    def initUI(self):
        """Create the physical shelves"""
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        grid = QtGui.QGridLayout()
        grid.setSpacing(100)

        for index, notebook in enumerate(self.notebooks):
            # distinguish between a notebook and a folder, stored as a tuple.
            # When encountering a folder, simply put a different image for the
            # moment.
            button = PicButton(QtGui.QPixmap(
                "./noteorganiser/assets/notebook-128.png"),
                notebook.strip(EXTENSION), 'notebook', self)
            button.setMinimumSize(128, 128)
            button.setMaximumSize(128, 128)
            button.clicked.connect(self.notebookClicked)
            grid.addWidget(button, 0, index)

        for index, folder in enumerate(self.folders):
            button = PicButton(QtGui.QPixmap(
                "./noteorganiser/assets/folder-128.png"),
                os.path.basename(folder), 'folder', self)
            button.setMinimumSize(128, 128)
            button.setMaximumSize(128, 128)
            button.clicked.connect(self.folderClicked)

            grid.addWidget(button, 1, index)

        self.layout().insertLayout(0, grid)

        # Create the navigation symbols
        hboxLayout = QtGui.QHBoxLayout()

        upButton = QtGui.QPushButton("&Up")
        upButton.clicked.connect(self.upFolder)

        hboxLayout.addWidget(upButton)
        hboxLayout.addStretch(1)

        self.layout().addStretch(1)
        self.layout().insertLayout(2, hboxLayout)

    def clearUI(self):
        for _ in range(3):
            layout = self.layout().takeAt(0)
            if isinstance(layout, QtGui.QLayout):
                self.clearLayout(layout)
                layout.deleteLater()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def addNotebook(self):
        """Add a new button"""
        self.parent.logger.info(
            'adding %s to the shelves' % self.notebooks[-1].strip(
                EXTENSION))
        self.clearUI()
        self.initUI()

    def removeNotebook(self, notebook):
        """
        Remove the notebook

        TODO: add a confirmation for non-empty notebooks
        """
        self.parent.logger.info(
            'deleting %s from the shelves' % notebook)
        path = os.path.join(self.level, notebook+EXTENSION)
        if os.stat(path).st_size != 0:
            print('Are you sure?')

        # Delete the file on the disk
        os.remove(path)

        # Delete the reference to the notebook
        index = self.notebooks.index(notebook+EXTENSION)
        self.notebooks.pop(index)

        # Redraw the graphical interface.
        self.clearUI()
        self.initUI()

    def notebookClicked(self):
        sender = self.sender()
        self.parent.logger.info('notebook '+sender.text+' button cliked')
        # Connect this to the switch tab focus to Editing
        self.parent.parent.switchTab('editing', sender.text)

    def folderClicked(self):
        sender = self.sender()
        self.parent.logger.info('folder '+sender.text+' button cliked')
        folder_path = os.path.join(self.parent.parent.root, sender.text)
        self.notebooks, self.folders = search_folder_recursively(
            self.parent.logger, folder_path)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.level = folder_path
        self.clearUI()
        self.initUI()

    def upFolder(self):
        if self.level == self.parent.root:
            return
        else:
            folder_path = os.path.dirname(self.level)
            self.notebooks, self.folders = search_folder_recursively(
                self.parent.logger, folder_path)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.level = folder_path
        self.clearUI()
        self.initUI()


class PicButton(QtGui.QPushButton):
    """Button with a picture"""
    def __init__(self, pixmap, text, style, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.parent = parent
        self.text = unicode(text)
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
        self.parent.removeNotebook(self.text)


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
