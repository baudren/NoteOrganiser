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


class Shelves(QtGui.QWidget):

    def __init__(self, notebooks, folders, parent=None):
        QtGui.QWidget.__init__(self, parent)
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

    def clearUI(self):
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


class NewNotebook(Dialog):

    def __init__(self, notebooks, parent=None):
        Dialog.__init__(self, parent)
        self.notebooks = notebooks
        self.names = [elem.strip(EXTENSION) for elem in notebooks]
        self.initUI()

    def initUI(self):
        self.logger.info("Creating popup window")

        self.setWindowTitle("New notebook")

        # Define the fields:
        # Name (text field)
        # type (so far, standard)
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        name = QtGui.QLabel("Notebook's name")
        self.name_entry = QtGui.QLineEdit()
        # Tick box that will be ticked when the name is long enough
        # TODO
        # The grid changes when some text is displayed here...
        self.name_confirmation_box = QtGui.QLabel("")

        # Query the type of notebook
        notebook_type_text = QtGui.QLabel("Notebook's type")
        notebook_type = QtGui.QComboBox()
        notebook_type.addItem("Standard")

        grid.addWidget(name, 0, 0)
        grid.addWidget(self.name_entry, 0, 1)
        grid.addWidget(notebook_type_text, 1, 0)
        grid.addWidget(notebook_type, 1, 1)

        # Add the "Create" button, as a confirmation, and the "Cancel" one
        create = QtGui.QPushButton("&Create")
        create.clicked.connect(self.create_notebook)
        cancel = QtGui.QPushButton("C&ancel")
        cancel.clicked.connect(self.clean_reject)

        grid.addWidget(create, 2, 0)
        grid.addWidget(cancel, 2, 1)
        grid.addWidget(self.name_confirmation_box, 3, 0)

        self.setLayout(grid)

    def create_notebook(self):
        """Query the entry fields and append the notebook list"""
        desired_name = self.name_entry.text()
        self.logger.info("Desired Notebook name: "+desired_name)
        if not desired_name or len(desired_name) < 2:
            self.name_confirmation_box.setText("name too short")
            self.logger.info("name rejected: too short")
        else:
            if desired_name in self.names:
                self.name_confirmation_box.setText(
                    "name already used")
                self.logger.info("name rejected: already used")
            else:
                # Actually creating the notebook
                self.notebooks.append(desired_name)
                self.name_confirmation_box.setText("Creating notebook")
                self.accept()


class NewEntry(Dialog):

    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.logger.info("Creating a 'New Entry' form")

        self.setWindowTitle("New entry")

        # Define global horizontal layout
        hboxLayout = QtGui.QHBoxLayout()

        # Define the fields: Name, tags and body
        formLayout = QtGui.QFormLayout()
        titleLineEdit = QtGui.QLineEdit()
        tagsLineEdit = QtGui.QLineEdit()
        corpusBox = QtGui.QTextEdit()

        formLayout.addRow(self.tr("&Title:"), titleLineEdit)
        formLayout.addRow(self.tr("Ta&gs:"), tagsLineEdit)
        formLayout.addRow(self.tr("&Body:"), corpusBox)

        hboxLayout.addLayout(formLayout)

        # Define the RHS with Ok, Cancel and list of tags TODO)
        vboxLayout = QtGui.QVBoxLayout()

        okButton = QtGui.QPushButton("&Ok")
        okButton.clicked.connect(self.creating_entry)
        cancelButton = QtGui.QPushButton("&Cancel")
        cancelButton.clicked.connect(self.clean_reject)

        vboxLayout.addWidget(okButton)
        vboxLayout.addWidget(cancelButton)

        hboxLayout.addLayout(vboxLayout)
        # Set the global layout
        self.setLayout(hboxLayout)

    def creating_entry(self):
        #TODO
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
