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


class NewNotebook(QtGui.QDialog):

    def __init__(self, notebooks, logger, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.logger = logger
        self.notebooks = notebooks
        self.initUI()

    def initUI(self):
        self.logger.info("Creating popup window")

        self.setWindowTitle("New notebook")

        # Define Ctrl+W to close it, and overwrite Esc
        _ = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+W'),
                            self, self.clean_accept)
        _ = QtGui.QShortcut(QtGui.QKeySequence('Esc'),
                            self, self.clean_reject)

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

    def clean_accept(self):
        """Logging the closing of the popup"""
        self.logger.info("Creating a new notebook!")
        self.accept()

    def clean_reject(self):
        """Logging the rejection of the popup"""
        self.logger.info("Aborting notebook creation")
        self.reject()

    def create_notebook(self):
        """Query the entry fields and append the notebook list"""
        desired_name = self.name_entry.text()
        self.logger.info("Desired Notebook name: "+desired_name)
        if not desired_name or len(desired_name) < 2:
            self.name_confirmation_box.setText("name too short")
            self.logger.info("name rejected: too short")
        else:
            if desired_name in self.notebooks:
                self.name_confirmation_box.setText(
                    "name already used")
                self.logger.info("name rejected: already used")
            else:
                # Actually creating the notebook
                self.notebooks.append(desired_name)
                self.name_confirmation_box.setText("Creating notebook")
                self.accept()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(window)

    button = PicButton(QtGui.QPixmap(
        "./noteorganiser/assets/notebook-128.png"))
    layout.addWidget(button)

    window.show()
    sys.exit(app.exec_())
