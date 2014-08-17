import sys
import os
from PySide import QtGui

from widgets import Shelves
from constants import EXTENSION


class ExampleFrame(QtGui.QFrame):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.show()


class CustomFrame(QtGui.QFrame):
    """
    Base class for all three tabbed frames
    """
    def __init__(self, parent=None):
        """ Create the basic layout """
        QtGui.QFrame.__init__(self, parent)
        # Create a shortcut notation for the list of notebooks
        self.parent = parent
        self.logger = parent.logger
        self.notebooks = self.parentWidget().notebooks
        self.folders = self.parentWidget().folders
        self.root = self.parentWidget().root

        self.initUI()

    def initUI(self):
        raise NotImplementedError


class Library(CustomFrame):
    """
    The notebooks will be stored and displayed there

    Should ressemble something like this:
     _________  _________  ____________
    / Library \/ Editing \/ Previewing \
    |          ----------------------------------
    |                              |            |
    |   notebook_1     notebook_2  | [+] new N  |
    | ------------------------------ [+] new F  |
    |                              | [-] delete |
    |   notebook_3                 |            |
    --------------------------------------------|
    """
    def initUI(self):
        self.logger.info("Starting UI init of %s" % self.__class__.__name__)
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        newNotebookButton = QtGui.QPushButton("&New Notebook")
        newNotebookButton.clicked.connect(self.parentWidget().create_notebook)

        newFolderButton = QtGui.QPushButton("New &Folder")
        newFolderButton.clicked.connect(self.parentWidget().create_folder)

        removeButton = QtGui.QPushButton("&Remove")
        self.shelves = Shelves(self.notebooks, self.folders, self)

        grid.addWidget(self.shelves, 0, 0, 5, 5)
        grid.addWidget(newNotebookButton, 1, 5)
        grid.addWidget(newFolderButton, 2, 5)
        grid.addWidget(removeButton, 3, 5)
        self.setLayout(grid)

        self.logger.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        self.shelves.add_notebook()


class Editing(CustomFrame):
    """
    Direct access to the markup files will be there

    The left hand side will be the text within a tab widget, named as the
    notebook it belongs to.

    Contrary to the Library tab, this one will have an additional state, the
    active state, which will dictate on which file the window is open.

     _________  _________  ____________
    / Library \/ Editing \/ Previewing \
    |----------           ----------------------------
    |    --------------------------|                  |
    |   /|                         | [+] new entry    |
    |   N|                         | [-] delete       |
    |   1|                         |                  |
    |   \|_________________________|                  |
    ---------------------------------------------------
    """
    def initUI(self):
        self.logger.info("Starting UI init of %s" % self.__class__.__name__)
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        newButton = QtGui.QPushButton("New entry", self)
        removeButton = QtGui.QPushButton("Remove", self)

        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition(QtGui.QTabWidget.West)

        for notebook in self.notebooks:
            text = QtGui.QTextEdit(self.tabs)
            source = open(os.path.join(self.root, notebook)).read()
            text.setText(source)
            text.setTabChangesFocus(True)
            self.tabs.addTab(text, notebook.strip(EXTENSION))

        vbox = QtGui.QVBoxLayout()

        vbox.addWidget(newButton)
        vbox.addWidget(removeButton)

        self.grid.addWidget(self.tabs, 0, 0)
        self.grid.addLayout(vbox, 0, 1)

        self.setLayout(self.grid)
        self.logger.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        """Adding files"""
        new = self.notebooks[-1]
        text = QtGui.QTextEdit(self.tabs)
        source = open(os.path.join(self.root, new)).read()
        text.setText(source)
        text.setTabChangesFocus(True)
        self.tabs.addTab(text, new.strip(EXTENSION))
        self.grid.removeWidget(self.tabs)
        self.grid.addWidget(self.tabs, 0, 0)

    def switchNotebook(self, notebook):
        """switching tab to desired notebook"""
        self.parent.logger.info("switching to "+notebook)
        index = self.notebooks.index(notebook+EXTENSION)
        self.tabs.setCurrentIndex(index)


if __name__ == "__main__":
    application = QtGui.QApplication(sys.argv)
    example = ExampleFrame()
    sys.exit(app.exec_())
