from __future__ import unicode_literals
from PySide import QtGui
from PySide import QtCore
import os

from .constants import EXTENSION


class Dialog(QtGui.QDialog):
    """
    Model for dialogs in Note Organiser (pop-up windows)

    """
    def __init__(self, parent=None):
        """Define the shortcuts"""
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.info = parent.info
        self.log = parent.log

        # Define Ctrl+W to close it, and overwrite Esc
        QtGui.QShortcut(QtGui.QKeySequence('Ctrl+W'),
                        self, self.clean_reject)
        QtGui.QShortcut(QtGui.QKeySequence('Esc'),
                        self, self.clean_reject)

        self.setLayout(QtGui.QVBoxLayout())

    def clean_accept(self):
        """Logging the closing of the popup"""
        self.log.info("%s form suceeded!" % self.__class__.__name__)
        self.accept()

    def clean_reject(self):
        """Logging the rejection of the popup"""
        self.log.info("Aborting %s form" % self.__class__.__name__)
        self.reject()

    def translate(self, string):
        """Temporary fix for unicode tr problems"""
        return string


class NewNotebook(Dialog):

    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.names = [os.path.splitext(elem)[0]
                      for elem in self.info.notebooks]
        self.initUI()

    def initUI(self):
        self.log.info("Creating a 'New Notebook' form")

        self.setWindowTitle("New notebook")

        # Define the fields:
        # Name (text field)
        # type (so far, standard)
        formLayout = QtGui.QFormLayout()
        self.nameLineEdit = QtGui.QLineEdit()
        # Query the type of notebook
        self.notebookType = QtGui.QComboBox()
        self.notebookType.addItem("Standard")

        formLayout.addRow(self.translate("Notebook's &name:"), self.nameLineEdit)
        formLayout.addRow(self.translate("&Notebook's &type:"), self.notebookType)
        self.layout().addLayout(formLayout)

        hboxLayout = QtGui.QHBoxLayout()

        # Add the "Create" button, as a confirmation, and the "Cancel" one
        self.createButton = QtGui.QPushButton("&Create")
        self.createButton.clicked.connect(self.createNotebook)
        self.cancelButton = QtGui.QPushButton("C&ancel")
        self.cancelButton.clicked.connect(self.clean_reject)

        # Add a spacer before so that the button do not stretch
        hboxLayout.addStretch()
        hboxLayout.addWidget(self.createButton)
        hboxLayout.addWidget(self.cancelButton)
        self.layout().addLayout(hboxLayout)

        # Create a status bar
        self.statusBar = QtGui.QStatusBar(self)
        self.layout().addWidget(self.statusBar)

    def createNotebook(self):
        """Query the entry fields and append the notebook list"""
        desired_name = str(self.nameLineEdit.text())
        self.log.info("Desired Notebook name: "+desired_name)
        if not desired_name or len(desired_name) < 2:
            self.statusBar.showMessage("name too short", 2000)
            self.log.info("name rejected: too short")
        else:
            if desired_name in self.names:
                self.statusBar.showMessage("name already used", 2000)
                self.log.info("name rejected: already used")
            else:
                # Actually creating the notebook
                self.info.notebooks.append(desired_name+EXTENSION)
                self.statusBar.showMessage("Creating notebook", 2000)
                self.accept()


class NewFolder(Dialog):

    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.names = [elem for elem in self.info.folders]
        self.initUI()

    def initUI(self):
        self.log.info("Creating a 'New Folder' form")
        self.setWindowTitle("New folder")

        # Define the field:
        # Name
        formLayout = QtGui.QFormLayout()
        self.nameLineEdit = QtGui.QLineEdit()

        formLayout.addRow(self.translate("Folder's &name:"), self.nameLineEdit)
        self.layout().addLayout(formLayout)

        buttonLayout = QtGui.QHBoxLayout()

        # Add the "Create" button, as a confirmation, and the "Cancel" one
        self.createButton = QtGui.QPushButton("&Create")
        self.createButton.clicked.connect(self.createFolder)
        self.cancelButton = QtGui.QPushButton("C&ancel")
        self.cancelButton.clicked.connect(self.clean_reject)

        buttonLayout.addStretch()
        buttonLayout.addWidget(self.createButton)
        buttonLayout.addWidget(self.cancelButton)
        self.layout().addLayout(buttonLayout)

        # Create a status bar
        self.statusBar = QtGui.QStatusBar()
        self.layout().addWidget(self.statusBar)

    def createFolder(self):
        desired_name = str(self.nameLineEdit.text())
        self.log.info("Desired Folder name: "+desired_name)
        if not desired_name or len(desired_name) < 2:
            self.statusBar.showMessage("name too short", 2000)
            self.log.info("name rejected: too short")
        else:
            if desired_name in self.names:
                self.statusBar.showMessage("name already used", 2000)
                self.log.info("name rejected, already used")
            else:
                # Actually creating the folder
                self.info.folders.append(desired_name)
                self.statusBar.showMessage("Creating Folder", 2000)
                self.accept()


class NewEntry(Dialog):
    """Create a new entry in the notebook"""

    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.log.info("Creating a 'New Entry' form")

        self.setWindowTitle("New entry")

        # Define the fields: Name, tags and body
        formLayout = QtGui.QFormLayout()
        self.titleLineEdit = QtGui.QLineEdit()
        self.tagsLineEdit = QtGui.QLineEdit()
        self.corpusBox = QtGui.QTextEdit()

        formLayout.addRow(self.translate("&Title:"), self.titleLineEdit)
        formLayout.addRow(self.translate("Ta&gs:"), self.tagsLineEdit)
        formLayout.addRow(self.translate("&Body:"), self.corpusBox)

        self.layout().addLayout(formLayout)

        # Define the RHS with Ok, Cancel and list of tags TODO)
        buttonLayout = QtGui.QHBoxLayout()

        self.okButton = QtGui.QPushButton("&Ok")
        self.okButton.clicked.connect(self.creating_entry)
        acceptShortcut = QtGui.QShortcut(
            QtGui.QKeySequence(self.translate("Shift+Enter")), self.corpusBox)
        acceptShortcut.activated.connect(self.creating_entry)

        self.cancelButton = QtGui.QPushButton("&Cancel")
        self.cancelButton.clicked.connect(self.clean_reject)

        # Add a spacer before so that the buttons do not stretch
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        self.layout().addLayout(buttonLayout)
        # Create the status bar
        self.statusBar = QtGui.QStatusBar(self)
        self.layout().addWidget(self.statusBar)

    def creating_entry(self):
        # Check if title is valid (non-empty)
        title = str(self.titleLineEdit.text())
        if not title or len(title) < 2:
            self.statusBar.showMessage(self.translate("Invalid title"), 2000)
            return
        tags = str(self.tagsLineEdit.text())
        if not tags or len(tags) < 2:
            self.statusBar.showMessage(self.translate("Invalid tags"), 2000)
            return
        tags = [tag.strip() for tag in tags.split(',')]
        corpus = self.corpusBox.toPlainText()
        if not corpus or len(corpus) < 2:
            self.statusBar.showMessage(self.translate("Empty entry"), 2000)
            return
        # Storing the variables to be recovered afterwards
        self.title = title
        self.tags = tags
        self.corpus = corpus
        self.clean_accept()


class SetExternalEditor(Dialog):

    """popup for setting the commandline for the external editor"""

    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.log.info("Creating a 'Set External Editor' form")

        self.setWindowTitle("Set External Editor")

        # Define the main window horizontal layout
        hboxLayout = QtGui.QHBoxLayout()

        # Define the field
        formLayout = QtGui.QFormLayout()
        self.commandlineEdit = QtGui.QLineEdit()

        self.commandlineEdit.setText(self.info.externalEditor)
        formLayout.addRow(self.tr("&external editor:"), self.commandlineEdit)

        hboxLayout.addLayout(formLayout)

        # Define the RHS with Ok, Cancel and list of tags TODO)
        buttonLayout = QtGui.QVBoxLayout()

        self.okButton = QtGui.QPushButton("&Ok")
        self.okButton.clicked.connect(self.set_commandline)

        self.cancelButton = QtGui.QPushButton("&Cancel")
        self.cancelButton.clicked.connect(self.clean_reject)

        buttonLayout.addStretch()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        hboxLayout.addLayout(buttonLayout)
        # Create the status bar
        self.statusBar = QtGui.QStatusBar(self)
        # Create a permanent widget displaying what we are doing
        statusWidget = \
            QtGui.QLabel("setting the commandline for the external editor")
        self.statusBar.addPermanentWidget(statusWidget)

        self.layout().addLayout(hboxLayout)
        self.layout().addWidget(self.statusBar)

    def set_commandline(self):
        """check the commandline write it to the settings and return"""
        # Check if text is a valid commandline
        commandline = str(self.commandlineEdit.text())
        if not commandline or len(commandline) < 2:
            self.statusBar.showMessage(self.tr("Invalid Commandline"), 2000)
            return
        # Storing the variables to be recovered afterwards
        self.commandline = commandline
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")
        self.settings.setValue("externalEditor", self.commandline)
        self.clean_accept()
