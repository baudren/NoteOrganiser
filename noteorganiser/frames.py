import os
from collections import OrderedDict as od
import pypandoc as pa

from PySide import QtGui
from PySide import QtCore
from PySide import QtWebKit

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
        raise NotImplementedError

    def clearUI(self):
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
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())


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
    loadNotebook = QtCore.Signal(str)

    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        newButton = QtGui.QPushButton("&New entry", self)
        newButton.clicked.connect(self.newEntry)

        # Edit in an exterior editor
        editButton = QtGui.QPushButton("&Edit (exterior editor)", self)

        # Launch the previewing
        previewButton = QtGui.QPushButton("&Preview notebook", self)
        previewButton.clicked.connect(self.preview)

        # Create the tabbed widgets
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition(QtGui.QTabWidget.West)

        for notebook in self.info.notebooks:
            editor = TextEditor(self)
            editor.setSource(os.path.join(self.info.level, notebook))

            self.tabs.addTab(editor, notebook.strip(EXTENSION))

        vbox = QtGui.QVBoxLayout()

        vbox.addWidget(newButton)
        vbox.addWidget(editButton)
        vbox.addWidget(previewButton)

        grid.addWidget(self.tabs, 0, 0)
        grid.addLayout(vbox, 0, 1)

        self.layout().addLayout(grid)

        self.log.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        """Redraw (time consuming...)"""
        self.clearUI()
        self.initUI()

    def switchNotebook(self, notebook):
        """switching tab to desired notebook"""
        self.log.info("switching to "+notebook)
        index = self.info.notebooks.index(notebook+EXTENSION)
        self.tabs.setCurrentIndex(index)

    def newEntry(self):
        """Open a form and store the results to the file"""
        self.popup = NewEntry(self)
        ok = self.popup.exec_()
        if ok:
            title = self.popup.title
            tags = self.popup.tags
            corpus = self.popup.corpus

            # Create the post
            post = tp.create_post_from_entry(title, tags, corpus)
            # recover the current editor
            editor = self.tabs.currentWidget()
            # Append the text
            editor.appendText(post)

    def preview(self):
        """Launch the previewing of the current notebook"""
        index = self.tabs.currentIndex()
        notebook = self.info.notebooks[index]
        self.log.info('ask to preview notebook %s' % notebook)
        self.loadNotebook.emit(notebook)


class Preview(CustomFrame):
    r"""
    Preview of the markdown in html, with tag selection

    The left hand side will be an html window, displaying the whole notebook.
    On the right, a list of tags will be displayed, as well as a calendar for
    date selection TODO


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

    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        self.layout().setDirection(QtGui.QBoxLayout.LeftToRight)

        # Left hand side: html window
        self.web = QtWebKit.QWebView(self)

        # Set the css file. Note that the path to the css needs to be absolute,
        # somehow...
        path = os.path.abspath(os.path.dirname(__file__))
        self.web.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile(
            os.path.join(path, 'assets', 'style', 'default.css')))

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
            for key, value in self.extracted_tags.iteritems():
                tag = QtGui.QPushButton(key)
                tag.setFlat(False)
                tag.setMinimumSize(100, 40+5*value)
                tag.setMaximumWidth(165)
                tag.setCheckable(True)
                if key in self.filters:
                    tag.setChecked(True)
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
            url, remaining_tags = self.convert(
                os.path.join(self.info.level, self.info.current_notebook),
                self.filters)
            # Grey out not useful buttons
            for key, button in self.tagButtons:
                if key in remaining_tags:
                    self.enableButton(button)
                else:
                    self.disableButton(button)
            self.setWebpage(url)

    def setWebpage(self, page):
        self.web.load(QtCore.QUrl(page))

    def loadNotebook(self, notebook, tags=[]):
        # Check the SHA1 sum to see if it has been computed already TODO
        # If not, compute it, recovering the list of tags, of dates TODO, and
        # the straight markdown file
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

        # save a temp. The basename will be modified to reflect the selection
        # of tags.
        base = os.path.basename(path)[:-len(EXTENSION)]
        if tags:
            base += '_'+'_'.join(tags)
        temp_path = os.path.join(self.temp_root, base+EXTENSION)
        self.log.debug('Creating temp file %s' % temp_path)
        with open(temp_path, 'w') as temp:
            temp.write('\n'.join(markdown))

        # Apply pandoc to this markdown file, from pypandoc thin wrapper, and
        # recover the html
        html = pa.convert(temp_path, 'html',
                          extra_args=['--highlight-style', 'pygments', '-s'])
        html = html.encode('utf-8')

        # Write the html to a file
        url = os.path.join(self.website_root, base+'.html')
        with open(url, 'w') as page:
            page.write(html)

        return url, remaining_tags

    def disableButton(self, button):
        button.setFlat(True)
        button.setCheckable(False)

    def enableButton(self, button):
        button.setFlat(False)
        button.setCheckable(True)


class Shelves(CustomFrame):
    refreshSignal = QtCore.Signal()
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
                notebook.strip(EXTENSION), 'notebook', self)
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

        self.upButton = QtGui.QPushButton("&Up")
        self.upButton.clicked.connect(self.upFolder)
        if self.info.level == self.info.root:
            self.upButton.setDisabled(True)

        self.newNotebookButton = QtGui.QPushButton("&New Notebook")
        self.newNotebookButton.clicked.connect(self.createNotebook)

        self.newFolderButton = QtGui.QPushButton("New &Folder")
        self.newFolderButton.clicked.connect(self.createFolder)

        hboxLayout.addWidget(self.upButton)
        hboxLayout.addWidget(self.newNotebookButton)
        hboxLayout.addWidget(self.newFolderButton)
        hboxLayout.addStretch(1)

        self.layout().addStretch(1)
        self.layout().insertLayout(2, hboxLayout)

    def clearUI(self):
        while self.layout().count():
            layout = self.layout().takeAt(0)
            if isinstance(layout, QtGui.QLayout):
                self.clearLayout(layout)
                layout.deleteLater()
        del self.buttons
        del self.upButton

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

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
            # Create an empty file (open and close)
            open(os.path.join(self.info.level, file_name), 'w').close()
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
            self.log, folder_path)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.info.level = folder_path
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
            self.log, folder_path)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.info.level = folder_path
        self.refresh()

    def upFolder(self):
        if self.info.level == self.info.root:
            return
        else:
            folder_path = os.path.dirname(self.info.level)
            self.info.notebooks, self.info.folders = search_folder_recursively(
                self.log, folder_path)
        # Update the current level as the folder_path, and refresh the content
        # of the window
        self.info.level = folder_path
        self.refresh()


class TextEditor(CustomFrame):
    """Custom text editor"""
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
        self.text = QtGui.QTextEdit()
        self.text.setTabChangesFocus(True)

        # Font
        self.font = QtGui.QFont()
        self.font.setFamily("Inconsolata")
        self.font.setStyleHint(QtGui.QFont.Monospace)
        self.font.setFixedPitch(True)
        self.font.setPointSize(14)

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
            text = open(self.source).read()
            self.text.setText(text)
            self.text.setTextCursor(oldCursor)
            self.text.ensureCursorVisible()

    def saveText(self):
        self.log.info("Writing modifications to %s" % self.source)
        text = self.text.toPlainText().encode('utf-8')
        with open(self.source, 'w') as file_handle:
            file_handle.write(text)

    def appendText(self, text):
        self.text.append('\n'+text)
        self.saveText()
