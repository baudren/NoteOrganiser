import sys
import os
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtGui import QAction, QTabWidget
from PySide.QtCore import Slot

# Local module imports
from frames import Library, Editing, Preview
from popups import NewNotebook
from logger import create_logger
import configuration as conf
from constants import EXTENSION


class NoteOrganiser(QMainWindow):
    """TODO"""

    states = [
        'library',  # The starting one, displaying the notebooks
        'editing',
        'preview']

    def __init__(self, info):
        QMainWindow.__init__(self)

        # Store reference to the info class
        self.info = info
        # Shortcut for the logger
        self.log = self.info.logger

        self.initUI()
        self.initLogic()
        self.show()

    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        self.initMenuBar()
        self.initStatusBar()
        self.initWidgets()
        self.log.info("Finished UI init of %s" % self.__class__.__name__)

        self.setGeometry(600, 1000, 1000, 600)
        self.setWindowTitle('Note Organiser')

    def initMenuBar(self):
        self.log.info("Creating Menu Bar")
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

    def initStatusBar(self):
        self.log.info("Creating Status Bar")
        self.statusBar()

    def initWidgets(self):
        # Creating the tabbed widget
        self.tabs = QTabWidget(self)

        # Creating the three tabs. Through their parent, they will recover the
        # reference to the list of notebooks.
        self.library = Library(self)
        self.editing = Editing(self)
        self.preview = Preview(self)

        # Adding them to the tabs widget
        self.tabs.addTab(self.library, "Library")
        self.tabs.addTab(self.editing, "Editing")
        self.tabs.addTab(self.preview, "Preview")

        # Set the tabs widget to be the center widget of the main window
        self.log.info("Setting the central widget")
        self.setCentralWidget(self.tabs)

    def initLogic(self):
        self.state = 'library'

    def switchTab(self, tab, notebook):
        self.tabs.setCurrentIndex(self.states.index(tab))
        if tab == 'editing':
            self.editing.switchNotebook(notebook)

    @Slot()
    def createNotebook(self):
        self.popup = NewNotebook(self)
        ok = self.popup.exec_()
        if ok:
            desired_name = self.info.notebooks[-1]
            self.log.info(desired_name+' is the desired name')
            file_name = desired_name
            # Create an empty file (open and close)
            open(os.path.join(self.info.level, file_name), 'w').close()
            # Refresh both the library and Editing tab.
            self.library.refresh()
            self.editing.refresh()

    @Slot()
    def createFolder(self):
        pass


def main(args):
    # Initialise the main Qt application
    application = QApplication(args)

    # Define a logger
    logger = create_logger('INFO')
    # Recover the folder path and the notebooks
    root, notebooks, folders = conf.initialise(logger)

    # Create an instance of the Information class to store all this.
    info = conf.Information(logger, root, notebooks, folders)

    # Define the main window
    main_window = NoteOrganiser(info)

    # Run
    sys.exit(application.exec_())


if __name__ == "__main__":
    main(sys.argv)
