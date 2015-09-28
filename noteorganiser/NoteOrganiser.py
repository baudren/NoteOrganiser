"""
.. module:: NoteOrganiser
    :synopsis: Define the NoteOrganiser class

.. moduleauthor:: Benjamin Audren <benjamin.audren@gmail.com>
"""
from __future__ import unicode_literals
# Main imports
import sys
import os
import re
from PySide import QtGui
from PySide import QtCore

# Local imports
from noteorganiser.popups import SetExternalEditor
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

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # Define a logger
        log_path = os.path.join(
            os.path.expanduser("~"), '.noteorganiser', 'log')
        logger = create_logger('INFO', 'file', log_path)
        # Recover the folder path and the notebooks
        root, notebooks, folders = conf.initialise(logger)

        # Create an instance of the Information class to store all this.
        info = conf.Information(logger, root, notebooks, folders)

        # Store reference to the info class
        self.info = info
        # Shortcut for the logger
        self.log = self.info.logger

        self.initUI()
        self.initLogic()
        self.show()

        # Show added the OS title bar, modifying the height of the window. It
        # is substracted below such that by default, if no previous
        # configuration was found, the window occupies the whole height.
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            # This function returns the available dimension excluding the
            # taskbar.
            geometry = QtGui.QApplication.desktop().availableGeometry()
            # We still have to remove the added height of OS title bar
            extra_height = self.frameGeometry().height() - self.geometry().height()
            extra_width = self.frameGeometry().width() - self.geometry().width()
            self.setGeometry(
                # TODO the 3./4 is a hack for windows (adds more space to the
                # top, probably not robust)
                extra_width/2, extra_height*3./4,
                (geometry.width()-extra_width)/2.,
                geometry.height()-extra_height)

    def initUI(self):
        """Initialise all the User Interface"""
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        self.initWidgets()
        self.initMenuBar()
        self.initStatusBar()
        self.log.info("Finished UI init of %s" % self.__class__.__name__)

        # set the window-icon
        path = os.path.abspath(os.path.dirname(__file__))
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(path, 'assets', 'notebook-128.png')))

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
        toggleEmptyAction.setStatusTip('Toggle the display of empty folders')
        toggleEmptyAction.setCheckable(True)
        toggleEmptyAction.setChecked(self.info.display_empty)
        toggleEmptyAction.triggered.connect(
            self.library.shelves.toggleDisplayEmpty)

        # Toggle refreshing of editor-page when file changes
        toggleRefreshAction = QtGui.QAction('automatically refresh editor',
            self)
        toggleRefreshAction.setStatusTip(
            'automatically refresh editor when the file changes')
        toggleRefreshAction.setCheckable(True)
        toggleRefreshAction.setChecked(self.info.refreshEditor)
        toggleRefreshAction.triggered.connect(
            self.toggleRefresh)

        # show popup for external editor commandline
        externalEditor = QtGui.QAction('set external Editor', self)
        externalEditor.setStatusTip(
            'Set the Commandline for the external Editor')
        externalEditor.triggered.connect(self.setExternalEditor)

        # Toggle use of Table of Content
        toggleUseTOC = QtGui.QAction('use TOC in output', self)
        toggleUseTOC.setStatusTip(
            'Toggle the usage of Table of Content in HTML-output')
        toggleUseTOC.setCheckable(True)
        toggleUseTOC.setChecked(self.info.use_TOC)
        toggleUseTOC.triggered.connect(self.toggleUseTOC)

        # Choose the main folder
        mainFolderAction = QtGui.QAction('change the main directory', self)
        mainFolderAction.setStatusTip(
            'Select another folder as the root level for the notebooks')
        mainFolderAction.triggered.connect(self.chooseMainFolder)

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
        optionsMenu.addAction(toggleRefreshAction)
        optionsMenu.addAction(externalEditor)
        optionsMenu.addAction(toggleUseTOC)
        optionsMenu.addAction(mainFolderAction)

        # Display menu
        displayMenu = menubar.addMenu('&Display')
        displayMenu.addAction(zoomInAction)
        displayMenu.addAction(zoomOutAction)
        displayMenu.addAction(resetSizeAction)

    def setExternalEditor(self):
        """set the variable for the external editor"""
        self.popup = SetExternalEditor(self)
        #this will show the popup
        ok = self.popup.exec_()
        # the return code is True if successfull
        if ok:
            #Recover the field
            self.info.externalEditor = self.popup.commandline

    def toggleRefresh(self):
        """
        toggle if the editor gets refreshed automatically when the file
        changes
        """
        #save settings
        self.info.refreshEditor = not self.info.refreshEditor
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")
        self.settings.setValue("refreshEditor", self.info.refreshEditor)
        if self.info.refreshEditor:
            self.log.info('auto refresh enabled')
        else:
            self.log.info('auto refresh disabled')

    def toggleUseTOC(self):
        """toggle the use of the Table of Content in html-output"""
        self.info.use_TOC = not self.info.use_TOC
        #save the setting
        self.settings = QtCore.QSettings("audren", "NoteOrganiser")
        self.settings.setValue("use_TOC", self.info.use_TOC)
        self.preview.reload()

    def chooseMainFolder(self):
        """Select another folder for the source of notebooks"""
        # Recover the folder path and the notebooks
        root, notebooks, folders = conf.initialise(
            self.log, force_folder_change=True)

        # Create an instance of the Information class to store all this.
        self.info.root = root
        self.info.level = root
        self.info.notebooks = notebooks
        self.info.folders = folders

        # Refresh the display of the current widget
        self.tabs.currentWidget().refresh()

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

        # adding additional shortcuts
        self.libraryShortcut = QtGui.QAction('library', self)
        self.libraryShortcut.setShortcut('Ctrl+L')
        self.libraryShortcut.triggered.connect(self.setActiveTab)
        self.addAction(self.libraryShortcut)
        self.editingShortcut = QtGui.QAction('editing', self)
        self.editingShortcut.setShortcut('Ctrl+E')
        self.editingShortcut.triggered.connect(self.setActiveTab)
        self.addAction(self.editingShortcut)
        self.previewShortcut = QtGui.QAction('preview', self)
        self.previewShortcut.setShortcut('Ctrl+W')
        self.previewShortcut.triggered.connect(self.setActiveTab)
        self.addAction(self.previewShortcut)

        # Set the tabs widget to be the center widget of the main window
        self.log.info("Setting the central widget")
        self.setCentralWidget(self.tabs)

        # show only the toolbar for the active tab
        self.tabs.currentChanged.connect(self.showActiveToolBar)

    def initLogic(self):
        """Linking signals from widgets to functions"""
        self.state = 'library'
        # Connect slots to signal
        # * shelves refresh to the editing refresh
        self.library.shelves.refreshSignal.connect(self.editing.refresh)
        # * shelves switchTab to the own switchTab method
        self.library.shelves.switchTabSignal.connect(self.switchTab)
        # * shelves preview signal to previewNotebook
        self.library.shelves.previewSignal.connect(self.previewNotebook)
        # * editing preview to preview loadNotebook, and switch the tab
        self.editing.loadNotebook.connect(self.previewNotebook)

    @QtCore.Slot(str, str)
    def switchTab(self, tab, notebook):
        """Switch Tab to the desired target"""
        self.tabs.setCurrentIndex(self.states.index(tab))
        if tab == 'editing':
            self.editing.switchNotebook(notebook)

    @QtCore.Slot(str)
    def previewNotebook(self, notebook):
        """Preview the desired notebook"""
        self.editing.switchNotebook(
            os.path.splitext(os.path.basename(notebook))[0])
        if self.preview.loadNotebook(notebook):
            self.switchTab('preview', notebook)

    def closeEvent(self, _):
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

    @QtCore.Slot(int)
    def showActiveToolBar(self, tabIndex):
        """show only the toolbar for the active tab"""
        getattr(self, self.states[tabIndex]).toolbar.setVisible(True)
        for index in range(len(self.states)):
            if index != tabIndex:
                getattr(self,
                        self.states[index]).toolbar.setVisible(False)

    def setActiveTab(self):
        """
        set the active tab in the tabWidget to the widget for which the
        shortcut was used
        """
        self.tabs.setCurrentWidget(getattr(self, self.sender().iconText()))


def main(args):
    """Create the application, and execute it"""
    # Initialise the main Qt application
    application = QtGui.QApplication(args)

    # Define the main window
    NoteOrganiser()

    # Run
    sys.exit(application.exec_())


if __name__ == "__main__":
    main(sys.argv)
