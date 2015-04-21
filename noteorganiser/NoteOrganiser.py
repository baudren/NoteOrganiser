"""
.. module:: NoteOrganiser
    :synopsis: Define the NoteOrganiser class

.. moduleauthor:: Benjamin Audren <benjamin.audren@gmail.com>
"""
from __future__ import unicode_literals
# Main imports
import sys
from PySide import QtGui
from PySide import QtCore

# Local imports
from noteorganiser.frames import Library, Editing, Preview
from noteorganiser.logger import create_logger
import noteorganiser.configuration as conf


class NoteOrganiser(QtGui.QMainWindow):
    """
    Main Program

    The main window will consist of three tabs, to help you navigate your
    notes: Library, editing and previewing.
    """
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
        """Initialise all the User Interface"""
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        self.initWidgets()
        self.initMenuBar()
        self.initStatusBar()
        self.log.info("Finished UI init of %s" % self.__class__.__name__)

        # set this to be half-screen, on the left
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            self.geometry = QtGui.QApplication.desktop().screenGeometry()
            self.setGeometry(
                0, 0, self.geometry.width()/2., self.geometry.height())
        self.setWindowTitle('Note Organiser')

    def initMenuBar(self):
        """Defining the menu bar"""
        self.log.info("Creating Menu Bar")
        # Exit
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.cleanClose)

        # Toggle displaying empty folders
        toggleEmptyAction = QtGui.QAction('display empty folders', self)
        toggleEmptyAction.setShortcut('Ctrl+T')
        toggleEmptyAction.setStatusTip('Toggle the display of empty folders')
        toggleEmptyAction.setCheckable(True)
        toggleEmptyAction.setChecked(self.info.display_empty)
        toggleEmptyAction.triggered.connect(
            self.library.shelves.toggleDisplayEmpty)

        # Zoom-in
        zoomInAction = QtGui.QAction('Zoom-in', self)
        zoomInAction.setShortcut('Ctrl++')
        zoomInAction.setStatusTip('Zoom in')
        zoomInAction.triggered.connect(self.zoomIn)

        # Zoom-out
        zoomOutAction = QtGui.QAction('Zoom-out', self)
        zoomOutAction.setShortcut('Ctrl+-')
        zoomOutAction.setStatusTip('Zoom out')
        zoomOutAction.triggered.connect(self.zoomOut)

        # Reset Size
        resetSizeAction = QtGui.QAction('Reset-size', self)
        resetSizeAction.setShortcut('Ctrl+0')
        resetSizeAction.setStatusTip('Reset size')
        resetSizeAction.triggered.connect(self.resetSize)

        # Create the menu
        menubar = self.menuBar()
        # File menu
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        # Options menu
        optionsMenu = menubar.addMenu('&Options')
        optionsMenu.addAction(toggleEmptyAction)

        # Display menu
        displayMenu = menubar.addMenu('&Display')
        displayMenu.addAction(zoomInAction)
        displayMenu.addAction(zoomOutAction)
        displayMenu.addAction(resetSizeAction)

    def initStatusBar(self):
        """Defining the status bar"""
        self.log.info("Creating Status Bar")
        self.statusBar()

    def initWidgets(self):
        """Creating the tabbed widget containing the three main tabs"""
        # Creating the tabbed widget
        self.tabs = QtGui.QTabWidget(self)

        # Creating the three tabs. Through their parent, they will recover the
        # reference to the list of notebooks.
        self.library = Library(self)
        self.editing = Editing(self)
        self.preview = Preview(self)

        # Adding them to the tabs widget
        self.tabs.addTab(self.library, "&Library")
        self.tabs.addTab(self.editing, "&Editing")
        self.tabs.addTab(self.preview, "Previe&w")

        # Set the tabs widget to be the center widget of the main window
        self.log.info("Setting the central widget")
        self.setCentralWidget(self.tabs)

    def initLogic(self):
        """Linking signals from widgets to functions"""
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
        """Switch Tab to the desired target"""
        self.tabs.setCurrentIndex(self.states.index(tab))
        if tab == 'editing':
            self.editing.switchNotebook(notebook)

    @QtCore.Slot(str)
    def previewNotebook(self, notebook):
        self.preview.loadNotebook(notebook)
        self.switchTab('preview', notebook)

    def closeEvent(self, event):
        self.cleanClose()

    def cleanClose(self):
        """Overload the closeEvent to store the geometry"""
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")
        self.settings.setValue("geometry", self.saveGeometry())
        self.close()

    def zoomIn(self):
        """send a zoom-in signal to the current tab"""
        self.tabs.currentWidget().zoomIn()

    def zoomOut(self):
        """send a zoom-out signal to the current tab"""
        self.tabs.currentWidget().zoomOut()

    def resetSize(self):
        self.tabs.currentWidget().resetSize()


def main(args):
    """Create the application, and execute it"""
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
