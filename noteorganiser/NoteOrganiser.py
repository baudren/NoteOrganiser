import sys
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtGui import QAction, QTabWidget
from PySide.QtGui import QFrame

# Local module imports
from frames import Library, Editing
from logger import create_logger
from configuration import initialise


class NoteOrganiser(QMainWindow):
    """TODO"""

    states = [
        'library',  # The starting one, displaying the notebooks
        'editing',
        'preview']

    def __init__(self, logger):
        QMainWindow.__init__(self)

        self.logger = logger
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
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

    def initStatusBar(self):
        self.statusBar()

    def initWidgets(self):
        # Creating the tabbed widget
        tabs = QTabWidget()

        # Creating the three tabs
        library = Library()
        editing = Editing()
        preview = QFrame()

        # Adding them to the tabs widget
        tabs.addTab(library, "Library")
        tabs.addTab(editing, "Editing")
        tabs.addTab(preview, "Preview")

        # Set the tabs widget to be the center widget of the main window
        self.setCentralWidget(tabs)

    def initLogic(self):
        self.state = 'library'


def main(args):
    # Define a logger
    logger = create_logger('INFO')

    # Recover the folder path and the notebooks
    root, notebooks = initialise(logger)
    application = QApplication(args)
    main_window = NoteOrganiser(logger)
    sys.exit(application.exec_())


if __name__ == "__main__":
    main(sys.argv)
