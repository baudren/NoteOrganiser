"""
.. module:: frames
    :synopsys: Define all the custom frames

.. moduleauthor:: Benjamin Audren <benjamin.audren@gmail.com>
"""
from __future__ import unicode_literals
import os
from collections import OrderedDict as od
import pypandoc as pa
import six  # Used to replace the od iteritems from py2
import io

from PySide import QtGui
from PySide import QtCore
from PySide import QtWebKit

# Local imports
from .popups import NewEntry, NewNotebook, NewFolder
import noteorganiser.text_processing as tp
from .constants import EXTENSION
from .configuration import search_folder_recursively
from .widgets import PicButton


class CustomFrame(QtGui.QFrame):
    """
    Base class for all three tabbed frames

    """
    def __init__(self, parent=None):
        """ Create the basic layout """
        QtGui.QFrame.__init__(self, parent)
        # Create a shortcut notation for the main information
        self.parent = parent
        self.info = parent.info
        self.log = parent.log

        # Create the main layout
        self.setLayout(QtGui.QVBoxLayout())

        if hasattr(self, 'initLogic'):
            self.initLogic()

        self.initUI()

    def initUI(self):
        """
        This will be called on creation

        A daughter class should implement this function
        """
        raise NotImplementedError

    def clearUI(self):
        """ Common method for recursively cleaning layouts """
        while self.layout().count():
            item = self.layout().takeAt(0)
            if isinstance(item, QtGui.QLayout):
                self.clearLayout(item)
                item.deleteLater()
            else:
                try:
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                except AttributeError:
                    pass

    def clearLayout(self, layout):
        """ Submethod to help cleaning the UI before redrawing """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def zoomIn(self):
        raise NotImplementedError

    def zoomOut(self):
        raise NotImplementedError

    def resetSize(self):
        raise NotImplementedError


class Library(CustomFrame):
    r"""
    The notebooks will be stored and displayed there

    Should ressemble something like this:
     _________  _________  _________
    / Library \/ Editing \/ Preview \
    |          ----------------------------------
    |                              | global tag |
    |   notebook_1     notebook_2  | another tag|
    | ------------------------------ tag taggy  |
    |                              | taggy tag  |
    |   notebook_3                 |            |
    |                              |            |
    | [up] [new N] [new F]         |            |
    --------------------------------------------|
    """
    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)

        # Create the shelves object
        self.shelves = Shelves(self)
        self.layout().addWidget(self.shelves)

        self.log.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        """ Refresh all elements of the frame """
        self.shelves.refresh()


class Editing(CustomFrame):
    r"""
    Direct access to the markup files will be there

    The left hand side will be the text within a tab widget, named as the
    notebook it belongs to.

    Contrary to the Library tab, this one will have an additional state, the
    active state, which will dictate on which file the window is open.

     _________  _________  _________
    / Library \/ Editing \/ Preview \
    |----------           ----------------------------
    |    --------------------------|                  |
    |   /|                         | [+] new entry    |
    |   N|                         | [ ] save document|
    |   1|                         | [ ] preview      |
    |   \|_________________________|                  |
    ---------------------------------------------------
    """
    # Launched when the previewer is desired
    loadNotebook = QtCore.Signal(str)

    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)

        # Global horizontal layout
        hbox = QtGui.QHBoxLayout()

        # New Entry Button to enter a new field in the current notebook
        self.newEntryButton = QtGui.QPushButton("&New entry", self)
        self.newEntryButton.clicked.connect(self.newEntry)

        # Edit in an exterior editor TODO
        self.editButton = QtGui.QPushButton("&Edit (exterior editor)", self)

        # Launch the previewing of the current notebook
        self.previewButton = QtGui.QPushButton("&Preview notebook", self)
        self.previewButton.clicked.connect(self.preview)

        # Create the tabbed widgets containing the text editors. The tabs will
        # appear on the left-hand side
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition(QtGui.QTabWidget.West)

        # The loop is over all the notebooks in the **current** folder
        for notebook in self.info.notebooks:
            editor = TextEditor(self)
            # Set the source of the TextEditor to the desired notebook
            editor.setSource(os.path.join(self.info.level, notebook))
            # Add the text editor to the tabbed area
            self.tabs.addTab(editor, os.path.splitext(notebook)[0])

        # Create the vertical layout for the right-hand side button
        vbox = QtGui.QVBoxLayout()

        vbox.addWidget(self.newEntryButton)
        vbox.addWidget(self.editButton)
        vbox.addWidget(self.previewButton)

        hbox.addWidget(self.tabs)
        hbox.addLayout(vbox)

        self.layout().addLayout(hbox)

        self.log.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        """Redraw the UI (time consuming...)"""
        self.clearUI()
        self.initUI()

    def switchNotebook(self, notebook):
        """switching tab to desired notebook"""
        self.log.info("switching to "+notebook)
        index = self.info.notebooks.index(notebook+EXTENSION)
        self.tabs.setCurrentIndex(index)

    def newEntry(self):
        """
        Open a form and store the results to the file

        .. note::
            this method does not save the file automatically

        """
        self.popup = NewEntry(self)
        # This will popup the popup
        ok = self.popup.exec_()
        # The return code is True if successful
        if ok:
            # Recover the three fields
            title = self.popup.title
            tags = self.popup.tags
            corpus = self.popup.corpus

            # Create the post
            post = tp.create_post_from_entry(title, tags, corpus)
            # recover the editor of the current widget, i.e. the open editor
            editor = self.tabs.currentWidget()
            # Append the text
            editor.appendText(post)

    def preview(self):
        """
        Launch the previewing of the current notebook

        Fires the loadNotebook signal with the desired notebook as an
        argument.
        """
        index = self.tabs.currentIndex()
        notebook = self.info.notebooks[index]
        self.log.info('ask to preview notebook %s' % notebook)
        self.loadNotebook.emit(notebook)

    def zoomIn(self):
        """
        So far only applies to the inside editor, and not the global fonts

        """
        # recover the current editor
        editor = self.tabs.currentWidget()
        editor.zoomIn()

    def zoomOut(self):
        # recover the current editor
        editor = self.tabs.currentWidget()
        editor.zoomOut()

    def resetSize(self):
        # recover the current editor
        editor = self.tabs.currentWidget()
        editor.resetSize()


class Preview(CustomFrame):
    r"""
    Preview of the markdown in html, with tag selection

    The left hand side will be an html window, displaying the whole notebook.
    On the right, a list of tags will be displayed.
    At some point, a calendar for date selection should also be displayed TODO

     _________  _________  _________
    / Library \/ Editing \/ Preview \
    |---------------------          ------------------
    |    --------------------------|                  |
    |    |                         | TAG1 TAG2 tag3   |
    |    |                         | tag4 ...         |
    |    |                         |                  |
    |    |_________________________| Calendar         |
    ---------------------------------------------------
    """
    def initLogic(self):
        """
        Create variables for storing local information

        """
        # Where to store the produced html pages
        self.website_root = os.path.join(self.info.level, '.website')
        # Where to store the temporary markdown files (maybe this step is not
        # necessary with pypandoc?)
        self.temp_root = os.path.join(self.info.level, '.temp')
        # Create the two folders if they do not already exist
        for path in (self.website_root, self.temp_root):
            if not os.path.isdir(path):
                os.mkdir(path)
        self.extracted_tags = od()
        self.filters = []

        # Shortcuts for resizing
        acceptShortcut = QtGui.QShortcut(
            QtGui.QKeySequence(self.tr("Ctrl+k")), self)
        acceptShortcut.activated.connect(self.zoomIn)

    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        self.layout().setDirection(QtGui.QBoxLayout.LeftToRight)

        # Left hand side: html window
        self.web = QtWebKit.QWebView(self)

        # Set the css file. Note that the path to the css needs to be absolute,
        # somehow...
        path = os.path.abspath(os.path.dirname(__file__))
        self.css = os.path.join(path, 'assets', 'style', 'default.css')
        self.web.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile(
            self.css))

        # The 1 stands for a stretch factor, set to 0 by default (seems to be
        # only for QWebView, though...
        self.layout().addWidget(self.web, 1)

        # Right hand side: Vertical layout for the tags inside a QScrollArea
        scrollArea = QtGui.QScrollArea()
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.verticalScrollBar().setFocusPolicy(QtCore.Qt.StrongFocus)

        # Need to create a dummy Widget, because QScrollArea can not accept a
        # layout, only a Widget
        dummy = QtGui.QWidget()
        # Limit its width
        dummy.setFixedWidth(200)

        vbox = QtGui.QVBoxLayout()
        self.tagButtons = []
        if self.extracted_tags:
            for key, value in six.iteritems(self.extracted_tags):
                tag = QtGui.QPushButton(key)
                tag.setFlat(False)
                tag.setMinimumSize(100, 40+5*value)
                tag.setMaximumWidth(165)
                tag.setCheckable(True)
                tag.clicked.connect(self.addFilter)
                self.tagButtons.append([key, tag])
                vbox.addWidget(tag)
        # Adding everything to the scroll area
        dummy.setLayout(vbox)
        scrollArea.setWidget(dummy)

        self.layout().addWidget(scrollArea)

        # Logging
        self.log.info("Finished UI init of %s" % self.__class__.__name__)

    def addFilter(self):
        """
        Filter out/in a certain tag

        From the status of the sender button, the associated tag will be
        added/removed from the filter.

        """
        sender = self.sender()
        if not sender.isFlat():
            if sender.isChecked():
                self.log.info('tag '+sender.text()+' added to the filter')
                self.filters.append(sender.text())
            else:
                self.log.info('tag '+sender.text()+' removed from the filter')
                self.filters.pop(self.filters.index(sender.text()))

            self.log.info("filter %s out of %s" % (
                ', '.join(self.filters), self.info.current_notebook))
            url, self.remaining_tags = self.convert(
                os.path.join(self.info.level, self.info.current_notebook),
                self.filters)
            # Grey out not useful buttons
            for key, button in self.tagButtons:
                if key in self.remaining_tags:
                    self.enableButton(button)
                else:
                    self.disableButton(button)
            self.setWebpage(url)

    def setWebpage(self, page):
        self.web.load(QtCore.QUrl(page))

    def loadNotebook(self, notebook, tags=[]):
        """
        Load a given markdown file as an html page

        """
        # TODO the dates should be recovered as well"
        self.initLogic()
        self.info.current_notebook = notebook
        self.log.info("Extracting markdown from %s" % notebook)

        url, tags = self.convert(
            os.path.join(self.info.level, notebook), tags)

        self.extracted_tags = tags
        # Finally, set the url of the web viewer to the desired page
        self.clearUI()
        self.initUI()
        self.setWebpage(url)

    def convert(self, path, tags):
        """
        Convert a notebook to html, with entries corresponding to the tags

        TODO: during the execution of this method, a check should be performed
        to verify if the file already exists, or maybe inside the convert
        function.

        Returns
        -------
        url : string
            path to the html page
        remaining_tags : OrderedDict
            dictionary of the remaining tags (the ones appearing in posts where
            all the selected tags where appearing, for further refinment)
        """
        markdown, remaining_tags = tp.from_notes_to_markdown(
            path, input_tags=tags)

        print('\n'.join(markdown))
        # save a temp. The basename will be modified to reflect the selection
        # of tags.
        base = os.path.basename(path)[:-len(EXTENSION)]
        if tags:
            base += '_'+'_'.join(tags)
        temp_path = os.path.join(self.temp_root, base+EXTENSION)
        self.log.debug('Creating temp file %s' % temp_path)
        with io.open(temp_path, 'w', encoding='utf-8') as temp:
            temp.write('\n'.join(markdown))

        bootstrap_min = (
            "http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/"
            "css/bootstrap.min.css")
        # Apply pandoc to this markdown file, from pypandoc thin wrapper, and
        # recover the html
        html = pa.convert(temp_path, 'html', encoding='utf-8',
                          extra_args=['--highlight-style', 'pygments', '-s',
                                      '-c', bootstrap_min,
                                      '-c', self.css])

        # Write the html to a file
        url = os.path.join(self.website_root, base+'.html')
        with io.open(url, 'w', encoding='utf-8') as page:
            page.write(html)

        return url, remaining_tags

    def disableButton(self, button):
        """ TODO: this should also alter the style """
        button.setFlat(True)
        button.setCheckable(False)

    def enableButton(self, button):
        """ TODO: this should also alter the style """
        button.setFlat(False)
        button.setCheckable(True)

    def zoomIn(self):
        multiplier = self.web.textSizeMultiplier()
        self.web.setTextSizeMultiplier(multiplier+0.1)

    def zoomOut(self):
        multiplier = self.web.textSizeMultiplier()
        self.web.setTextSizeMultiplier(multiplier-0.1)

    def resetSize(self):
        self.web.setTextSizeMultiplier(1)


class Shelves(CustomFrame):
    """
    Custom display of the notebooks and folder

    """
    # Fired when a change is made, so that the Editing panel can also adapt
    refreshSignal = QtCore.Signal()
    # Fired when a notebook is clicked, to navigate to the editor.
    # TODO also define as a shift+click to directly open the previewer
    switchTabSignal = QtCore.Signal(str, str)

    def initUI(self):
        """Create the physical shelves"""
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        grid = QtGui.QGridLayout()
        grid.setSpacing(100)
        path = os.path.dirname(__file__)
        self.buttons = []

        for index, notebook in enumerate(self.info.notebooks):
            # distinguish between a notebook and a folder, stored as a tuple.
            # When encountering a folder, simply put a different image for the
            # moment.
            button = PicButton(
                QtGui.QPixmap(
                    os.path.join(path, 'assets', 'notebook-128.png')),
                os.path.splitext(notebook)[0], 'notebook', self)
            button.setMinimumSize(128, 128)
            button.setMaximumSize(128, 128)
            button.clicked.connect(self.notebookClicked)
            button.deleteNotebook.connect(self.removeNotebook)
            self.buttons.append(button)

            grid.addWidget(button, 0, index)

        for index, folder in enumerate(self.info.folders):
            button = PicButton(
                QtGui.QPixmap(
                    os.path.join(path, 'assets', 'folder-128.png')),
                os.path.basename(folder), 'folder', self)
            button.setMinimumSize(128, 128)
            button.setMaximumSize(128, 128)
            button.clicked.connect(self.folderClicked)
            self.buttons.append(button)

            grid.addWidget(button, 1, index)

        self.layout().insertLayout(0, grid)

        # Create the navigation symbols
        hboxLayout = QtGui.QHBoxLayout()

        # Go up in the directories (disabled if in the root directory)
        self.upButton = QtGui.QPushButton("&Up")
        self.upButton.clicked.connect(self.upFolder)
        if self.info.level == self.info.root:
            self.upButton.setDisabled(True)

        # Create a new notebook
        self.newNotebookButton = QtGui.QPushButton("&New Notebook")
        self.newNotebookButton.clicked.connect(self.createNotebook)

        # Create a new folder
        self.newFolderButton = QtGui.QPushButton("New &Folder")
        self.newFolderButton.clicked.connect(self.createFolder)

        # Toggle between displaying and hiding empty folders
        self.toggleDisplayFoldersButton = QtGui.QPushButton(
            "&Toggle Display Empty Folder")
        self.toggleDisplayFoldersButton.clicked.connect(
            self.toggleDisplayEmpty)

        hboxLayout.addWidget(self.upButton)
        hboxLayout.addWidget(self.newNotebookButton)
        hboxLayout.addWidget(self.newFolderButton)
        hboxLayout.addStretch(1)
        hboxLayout.addWidget(self.toggleDisplayFoldersButton)

        self.layout().addStretch(1)
        self.layout().insertLayout(2, hboxLayout)

    def refresh(self):
        # Redraw the graphical interface.
        self.clearUI()
        self.initUI()

        # Broadcast a refreshSignal order
        self.refreshSignal.emit()

    def createNotebook(self):
        self.popup = NewNotebook(self)
        ok = self.popup.exec_()
        if ok:
            desired_name = self.info.notebooks[-1]
            self.log.info(desired_name+' is the desired name')
            file_name = desired_name
            # Create a file, containing only the title
            with io.open(os.path.join(self.info.level, file_name),
                         'w', encoding='utf-8') as notebook:
                clean_name = os.path.splitext(desired_name)[0]
                notebook.write(clean_name.capitalize()+'\n')
                notebook.write(''.join(['=' for letter in clean_name]))
                notebook.write('\n\n')
            # Refresh both the library and Editing tab.
            self.refresh()

    def createFolder(self):
        self.popup = NewFolder(self)
        ok = self.popup.exec_()
        if ok:
            desired_name = self.info.folders[-1]
            self.log.info(desired_name+' is the desired name')
            folder_name = desired_name
            # Create the folder
            try:
                os.mkdir(os.path.join(self.info.level, folder_name))
            except OSError:
                # If it already exists, continue
                pass
        # Change the level to the newly created folder, and send a refresh
        # TODO display a warning that an empty folder will be discared if
        # browsed out.
        folder_path = os.path.join(self.info.root, folder_name)
        self.info.notebooks, self.info.folders = search_folder_recursively(
            self.log, folder_path, self.info.display_empty)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.info.level = folder_path
        self.refresh()

    def toggleDisplayEmpty(self):
        self.info.display_empty = not self.info.display_empty
        # Read again the current folder
        self.info.notebooks, self.info.folders = search_folder_recursively(
            self.log, self.info.level, self.info.display_empty)
        self.refresh()

    @QtCore.Slot(str)
    def removeNotebook(self, notebook):
        """
        Remove the notebook

        """
        self.log.info(
            'deleting %s from the shelves' % notebook)
        path = os.path.join(self.info.level, notebook+EXTENSION)

        # Assert that the file is empty, or ask for confirmation
        if os.stat(path).st_size != 0:
            self.reply = QtGui.QMessageBox.question(
                self, 'Message',
                "Are you sure you want to delete %s?" % notebook,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)
        else:
            self.reply = QtGui.QMessageBox.Yes

        if self.reply == QtGui.QMessageBox.Yes:
            os.remove(path)
            # Delete the reference to the notebook
            index = self.info.notebooks.index(notebook+EXTENSION)
            self.info.notebooks.pop(index)

            # Refresh the display
            self.refresh()

        else:
            self.log.info("Aborting")

    def notebookClicked(self):
        sender = self.sender()
        self.log.info('notebook '+sender.text+' button cliked')
        # Emit a signal asking for changing the tab
        self.switchTabSignal.emit('editing', sender.text)

    def folderClicked(self):
        sender = self.sender()
        self.log.info('folder '+sender.text+' button cliked')
        folder_path = os.path.join(self.info.root, sender.text)
        self.info.notebooks, self.info.folders = search_folder_recursively(
            self.log, folder_path, self.info.display_empty)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.info.level = folder_path
        self.refresh()

    def upFolder(self):
        folder_path = os.path.dirname(self.info.level)
        self.info.notebooks, self.info.folders = search_folder_recursively(
            self.log, folder_path, self.info.display_empty)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.info.level = folder_path
        self.refresh()


class TextEditor(CustomFrame):
    """Custom text editor"""
    defaultFontSize = 14

    def initUI(self):
        """top menu bar and the text area"""
        # Menu bar
        menuBar = QtGui.QHBoxLayout()

        self.saveButton = QtGui.QPushButton("&Save", self)
        self.saveButton.clicked.connect(self.saveText)

        self.readButton = QtGui.QPushButton("&Reload", self)
        self.readButton.clicked.connect(self.loadText)

        menuBar.addWidget(self.saveButton)
        menuBar.addWidget(self.readButton)
        menuBar.addStretch(1)

        self.layout().addLayout(menuBar)

        # Text
        self.text = CustomTextEdit()
        self.text.setTabChangesFocus(True)

        # Font
        self.font = QtGui.QFont()
        self.font.setFamily("Inconsolata")
        self.font.setStyleHint(QtGui.QFont.Monospace)
        self.font.setFixedPitch(True)
        self.font.setPointSize(self.defaultFontSize)

        self.text.setFont(self.font)
        self.layout().addWidget(self.text)

    def setSource(self, source):
        self.log.info("Reading %s" % source)
        self.source = source
        self.loadText()

    def loadText(self):
        if self.source:
            # Store the last cursor position
            oldCursor = self.text.textCursor()
            text = io.open(self.source, 'r').read()
            self.text.setText(text)
            self.text.setTextCursor(oldCursor)
            self.text.ensureCursorVisible()

    def saveText(self):
        self.log.info("Writing modifications to %s" % self.source)
        text = self.text.toPlainText()
        with io.open(self.source, 'w', encoding='utf-8') as file_handle:
            file_handle.write(text)


    def appendText(self, text):
        self.text.append('\n'+text)
        self.saveText()

    def zoomIn(self):
        size = self.font.pointSize()
        self.font.setPointSize(size+1)
        self.text.setFont(self.font)

    def zoomOut(self):
        size = self.font.pointSize()
        self.font.setPointSize(size-1)
        self.text.setFont(self.font)

    def resetSize(self):
        self.font.setPointSize(self.defaultFontSize)
        self.text.setFont(self.font)


class CustomTextEdit(QtGui.QTextEdit):

    def toPlainText(self):
        text = QtGui.QTextEdit.toPlainText(self)
        if isinstance(text, bytes):
            text = str(text)
        return text
