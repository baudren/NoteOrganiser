import sys
import os
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtGui import QAction, QTabWidget
from PySide.QtGui import QFrame
from PySide.QtCore import Slot

# Local module imports
from frames import Library, Editing
from widgets import NewNotebook
from logger import create_logger
from configuration import initialise
from constants import EXTENSION


class NoteOrganiser(QMainWindow):
    """TODO"""

    states = [
        'library',  # The starting one, displaying the notebooks
        'editing',
        'preview']

    def __init__(self, logger, root, notebooks, folders):
        QMainWindow.__init__(self)

        # Store references to the logger, root folder and the entire list of
        # notebooks extracted from the configuration stage.
        self.logger = logger
        self.root = root
        self.notebooks = notebooks
        self.folders = folders

        self.initUI()
        self.initLogic()
        self.show()

    def initUI(self):
        self.logger.info("Starting UI init of %s" % self.__class__.__name__)
        self.initMenuBar()
        self.initStatusBar()
        self.initWidgets()
        self.logger.info("Finished UI init of %s" % self.__class__.__name__)

        self.setGeometry(600, 1000, 1000, 600)
        self.setWindowTitle('Note Organiser')

    def initMenuBar(self):
        self.logger.info("Creating Menu Bar")
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

    def initStatusBar(self):
        self.logger.info("Creating Status Bar")
        self.statusBar()

    def initWidgets(self):
        # Creating the tabbed widget
        self.tabs = QTabWidget(self)

        # Creating the three tabs. Through their parent, they will recover the
        # reference to the list of notebooks.
        self.library = Library(self)
        self.editing = Editing(self)
        self.preview = QFrame(self)

        # Adding them to the tabs widget
        self.tabs.addTab(self.library, "Library")
        self.tabs.addTab(self.editing, "Editing")
        self.tabs.addTab(self.preview, "Preview")

        # Set the tabs widget to be the center widget of the main window
        self.logger.info("Setting the central widget")
        self.setCentralWidget(self.tabs)

    def initLogic(self):
        self.state = 'library'

    def switchTab(self, tab, notebook):
        self.tabs.setCurrentIndex(self.states.index(tab))
        if tab == 'editing':
            self.editing.switchNotebook(notebook)

    @Slot()
    def create_notebook(self):
        self.popup = NewNotebook(self.notebooks, self)
        ok = self.popup.exec_()
        if ok:
            desired_name = self.popup.notebooks.pop()
            self.logger.info(desired_name+' is the desired name')
            file_name = desired_name+EXTENSION
            # Create an empty file (open and close)
            open(os.path.join(self.root, file_name), 'w').close()
            # Append the file name to the list of notebooks
            self.notebooks.append(file_name)
            # Refresh both the library and Editing tab.
            self.library.refresh()
            self.editing.refresh()

    @Slot()
    def create_folder(self):
        pass


def main(args):
    # Initialise the main Qt application
    application = QApplication(args)

    # Define a logger
    logger = create_logger('INFO')
    # Recover the folder path and the notebooks
    root, notebooks, folders = initialise(logger)
    # Define the main window
    main_window = NoteOrganiser(logger, root, notebooks, folders)

    # Run
    sys.exit(application.exec_())


if __name__ == "__main__":
    main(sys.argv)
