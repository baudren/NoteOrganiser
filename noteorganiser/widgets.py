import sys
import os
from PySide import QtGui
from PySide import QtCore
from constants import EXTENSION
from configuration import search_folder_recursively


class Dialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.logger = parent.logger

        # Define Ctrl+W to close it, and overwrite Esc
        _ = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+W'),
                            self, self.clean_accept)
        _ = QtGui.QShortcut(QtGui.QKeySequence('Esc'),
                            self, self.clean_reject)

    def clean_accept(self):
        """Logging the closing of the popup"""
        self.logger.info("%s form suceeded!" % self.__class__.__name__)
        self.accept()

    def clean_reject(self):
        """Logging the rejection of the popup"""
        self.logger.info("Aborting %s form" % self.__class__.__name__)
        self.reject()


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
                notebook.strip(EXTENSION))
            button.setMinimumSize(128, 128)
            button.setMaximumSize(128, 128)
            button.clicked.connect(self.notebookClicked)
            grid.addWidget(button, 0, index)

        for index, folder in enumerate(self.folders):
            button = PicButton(QtGui.QPixmap(
                "./noteorganiser/assets/folder-128.png"),
                os.path.basename(folder))
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

        self.layout().insertLayout(1, hboxLayout)

    def clearUI(self):
        for _ in range(2):
            layout = self.layout().takeAt(0)
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

    def add_notebook(self):
        """Add a new button"""
        self.parent.logger.info(
            'adding %s to the shelves' % self.notebooks[-1].strip(
                EXTENSION))
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


class NewNotebook(Dialog):

    def __init__(self, notebooks, parent=None):
        Dialog.__init__(self, parent)
        self.notebooks = notebooks
        self.names = [elem.strip(EXTENSION) for elem in notebooks]
        self.initUI()

    def initUI(self):
        self.logger.info("Creating a 'New Notebook' form")

        self.setWindowTitle("New notebook")

        # Define global vertical layout
        vboxLayout = QtGui.QVBoxLayout()

        # Define the fields:
        # Name (text field)
        # type (so far, standard)
        formLayout = QtGui.QFormLayout()
        self.nameLineEdit = QtGui.QLineEdit()
        # Query the type of notebook
        self.notebookType = QtGui.QComboBox()
        self.notebookType.addItem("Standard")

        formLayout.addRow(self.tr("Notebook's &name:"), self.nameLineEdit)
        formLayout.addRow(self.tr("&Notebook's &type:"), self.notebookType)
        vboxLayout.addLayout(formLayout)

        hboxLayout = QtGui.QHBoxLayout()

        # Add the "Create" button, as a confirmation, and the "Cancel" one
        create = QtGui.QPushButton("&Create")
        create.clicked.connect(self.create_notebook)
        cancel = QtGui.QPushButton("C&ancel")
        cancel.clicked.connect(self.clean_reject)
        hboxLayout.addWidget(create)
        hboxLayout.addWidget(cancel)
        vboxLayout.addLayout(hboxLayout)

        # Create a status bar
        self.statusBar = QtGui.QStatusBar()
        vboxLayout.addWidget(self.statusBar)

        self.setLayout(vboxLayout)

    def create_notebook(self):
        """Query the entry fields and append the notebook list"""
        desired_name = self.nameLineEdit.text()
        self.logger.info("Desired Notebook name: "+desired_name)
        if not desired_name or len(desired_name) < 2:
            self.statusBar.showMessage("name too short", 2000)
            self.logger.info("name rejected: too short")
        else:
            if desired_name in self.names:
                self.statusBar.showMessage("name already used", 2000)
                self.logger.info("name rejected: already used")
            else:
                # Actually creating the notebook
                self.notebooks.append(desired_name)
                self.statusBar.showMessage("Creating notebook", 2000)
                self.accept()


class NewEntry(Dialog):

    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.logger.info("Creating a 'New Entry' form")

        self.setWindowTitle("New entry")

        # Define global vertical layout
        vboxLayout = QtGui.QVBoxLayout()

        # Define the main window horizontal layout
        hboxLayout = QtGui.QHBoxLayout()

        # Define the fields: Name, tags and body
        formLayout = QtGui.QFormLayout()
        self.titleLineEdit = QtGui.QLineEdit()
        self.tagsLineEdit = QtGui.QLineEdit()
        self.corpusBox = QtGui.QTextEdit()

        formLayout.addRow(self.tr("&Title:"), self.titleLineEdit)
        formLayout.addRow(self.tr("Ta&gs:"), self.tagsLineEdit)
        formLayout.addRow(self.tr("&Body:"), self.corpusBox)

        hboxLayout.addLayout(formLayout)

        # Define the RHS with Ok, Cancel and list of tags TODO)
        buttonLayout = QtGui.QVBoxLayout()

        okButton = QtGui.QPushButton("Ok")
        okButton.clicked.connect(self.creating_entry)
        acceptShortcut = QtGui.QShortcut(
            QtGui.QKeySequence(self.tr("Shift+Enter")), self.corpusBox)
        acceptShortcut.activated.connect(self.creating_entry)

        cancelButton = QtGui.QPushButton("&Cancel")
        cancelButton.clicked.connect(self.clean_reject)

        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        hboxLayout.addLayout(buttonLayout)
        # Create the status bar
        self.statusBar = QtGui.QStatusBar(self)
        # Create a permanent widget displaying what we are doing
        statusWidget = QtGui.QLabel("Creating new entry")
        self.statusBar.addPermanentWidget(statusWidget)

        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.statusBar)

        # Set the global layout
        self.setLayout(vboxLayout)

    def creating_entry(self):
        # Check if title is valid (non-empty)
        title = self.titleLineEdit.text()
        if not title or len(title) < 2:
            self.statusBar.showMessage(self.tr("Invalid title"), 2000)
            return
        tags = self.tagsLineEdit.text()
        if not tags or len(tags) < 2:
            self.statusBar.showMessage(self.tr("Invalid tags"), 2000)
            return
        corpus = self.corpusBox.toPlainText()
        if not corpus or len(corpus) < 2:
            self.statusBar.showMessage(self.tr("Empty entry"), 2000)
            return
        # Storing the variables to be recovered afterwards
        self.title = title
        self.tags = tags
        self.corpus = corpus
        self.clean_accept()


class PicButton(QtGui.QPushButton):
    """Button with a picture"""
    def __init__(self, pixmap, text, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.text = unicode(text)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)
        painter.drawText(event.rect(), self.text)

    def sizeHint(self):
        return self.pixmap.size()

    def mouseReleaseEvent(self, ev):
        """Define a behaviour under click"""
        self.click()
        #self.emit(QtCore.SIGNAL('clicked()'))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(window)

    button = PicButton(QtGui.QPixmap(
        "./noteorganiser/assets/notebook-128.png"), 'something')
    layout.addWidget(button)

    window.show()
    sys.exit(app.exec_())
