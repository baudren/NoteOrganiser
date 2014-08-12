import sys
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtGui import QAction, QTabWidget
from PySide.QtGui import QFrame
from PySide.QtCore import Slot

# Local module imports
from frames import Library, Editing
from widgets import NewNotebook
from logger import create_logger
from configuration import initialise


class NoteOrganiser(QMainWindow):
    """TODO"""

    states = [
        'library',  # The starting one, displaying the notebooks
        'editing',
        'preview']

    def __init__(self, logger, root, notebooks):
        QMainWindow.__init__(self)

        # Store references to the logger, root folder and the entire list of
        # notebooks extracted from the configuration stage.
        self.logger = logger
        self.root = root
        self.notebooks = notebooks

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
        tabs = QTabWidget(self)

        # Creating the three tabs. Through their parent, they will recover the
        # reference to the list of notebooks.
        library = Library(self)
        editing = Editing(self)
        preview = QFrame(self)

        # Adding them to the tabs widget
        tabs.addTab(library, "Library")
        tabs.addTab(editing, "Editing")
        tabs.addTab(preview, "Preview")

        # Set the tabs widget to be the center widget of the main window
        self.logger.info("Setting the central widget")
        self.setCentralWidget(tabs)

    def initLogic(self):
        self.state = 'library'

    @Slot()
    def create_notebook(self):
        self.popup = NewNotebook(self.notebooks, self.logger)
        ok = self.popup.exec_()
        #self.popup.raise_()
        if ok:
            self.logger.info(self.popup.notebooks[-1]+' is the desired name')
        #self.popup.activateWindow()
        print self.popup.notebooks

    @Slot()
    def create_folder(self):
        pass


def main(args):
    # Initialise the main Qt application
    application = QApplication(args)

    # Define a logger
    logger = create_logger('INFO')
    # Recover the folder path and the notebooks
    root, notebooks = initialise(logger)
    # Define the main window
    main_window = NoteOrganiser(logger, root, notebooks)

    # Run
    sys.exit(application.exec_())


if __name__ == "__main__":
    main(sys.argv)
