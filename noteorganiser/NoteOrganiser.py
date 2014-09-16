import sys
import os
from PySide import QtGui
from PySide import QtCore

# Local module imports
from noteorganiser.frames import Library, Editing, Preview
from noteorganiser.popups import NewNotebook
from noteorganiser.logger import create_logger
import noteorganiser.configuration as conf


class NoteOrganiser(QtGui.QMainWindow):
    """TODO"""

    states = [
        'library',  # The starting one, displaying the notebooks
        'editing',
        'preview']

    def __init__(self, info):
        QtGui.QMainWindow.__init__(self)

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

        # TODO set this to be half-screen, on the right
        self.setGeometry(600, 1000, 1000, 600)
        self.setWindowTitle('Note Organiser')

    def initMenuBar(self):
        self.log.info("Creating Menu Bar")
        exitAction = QtGui.QAction('&Exit', self)
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
        self.tabs = QtGui.QTabWidget(self)

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
        # Connect slots to signal
        # * shelves refresh to the editing refresh
        self.library.shelves.refreshSignal.connect(self.editing.refresh)
        # * shelves switchTab to the own switchTab method
        self.library.shelves.switchTabSignal.connect(self.switchTab)
        # * editing preview to preview loadNotebook, and switch the the tab
        self.editing.loadNotebook.connect(self.previewNotebook)

    @QtCore.Slot(str, str)
    def switchTab(self, tab, notebook):
        self.tabs.setCurrentIndex(self.states.index(tab))
        if tab == 'editing':
            self.editing.switchNotebook(notebook)

    @QtCore.Slot(str)
    def previewNotebook(self, notebook):
        self.preview.loadNotebook(notebook)
        self.switchTab('preview', notebook)


def main(args):
    # Initialise the main Qt application
    application = QtGui.QApplication(args)

    # Define a logger
    logger = create_logger('INFO', 'file')
    # Recover the folder path and the notebooks
    root, notebooks, folders = conf.initialise(logger)

    # Create an instance of the Information class to store all this.
    info = conf.Information(logger, root, notebooks, folders)

    # Define the main window
    NoteOrganiser(info)

    # Run
    sys.exit(application.exec_())


if __name__ == "__main__":
    main(sys.argv)
