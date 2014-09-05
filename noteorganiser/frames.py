import sys
import os
import pypandoc as pa

from PySide import QtGui
from PySide import QtCore
from PySide import QtWebKit

from widgets import Shelves, TextEditor
from popups import NewEntry
import text_processing as tp
from constants import EXTENSION


class ExampleFrame(QtGui.QFrame):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.show()


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

    def clearUI(self, number):
        for _ in range(number):
            layout = self.layout().takeAt(0)
            if isinstance(layout, QtGui.QLayout):
                self.clearLayout(layout)
                layout.deleteLater()

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
    |                              |            |
    |   notebook_1     notebook_2  | [+] new N  |
    | ------------------------------ [+] new F  |
    |                              | [-] delete |
    |   notebook_3                 |            |
    --------------------------------------------|
    """
    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)

        # Grid Layout
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        newNotebookButton = QtGui.QPushButton("&New Notebook")
        newNotebookButton.clicked.connect(self.parentWidget().create_notebook)

        newFolderButton = QtGui.QPushButton("New &Folder")
        newFolderButton.clicked.connect(self.parentWidget().create_folder)

        removeButton = QtGui.QPushButton("&Remove")

        # Create the shelves object
        self.shelves = Shelves(self)

        grid.addWidget(self.shelves, 0, 0, 5, 5)
        grid.addWidget(newNotebookButton, 1, 5)
        grid.addWidget(newFolderButton, 2, 5)
        grid.addWidget(removeButton, 3, 5)

        self.layout().addLayout(grid)

        self.log.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        self.shelves.addNotebook()


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

        QtGui.QTextDocument
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
        self.clearUI(2)
        self.initUI()

    def switchNotebook(self, notebook):
        """switching tab to desired notebook"""
        self.parent.log.info("switching to "+notebook)
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
        self.parent.preview.loadNotebook(notebook)
        self.parent.switchTab('preview', notebook)


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
        self.website_root = os.path.join(self.info.level, '.website')
        if not os.path.isdir(self.website_root):
            os.mkdir(self.website_root)
        self.sha = []
        self.extracted_tags = []

    def initUI(self):
        self.log.info("Starting UI init of %s" % self.__class__.__name__)
        self.layout().setDirection(QtGui.QBoxLayout.LeftToRight)

        # Left hand side: html window
        self.web = QtWebKit.QWebView(self)
        # Set the css file. Note that the path to the css needs to be absolute,
        # somehow...
        local_path = os.getcwd()
        self.web.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile(
            os.path.join(local_path, 'noteorganiser', 'assets', 'style',
                         'default.css')))

        self.layout().addWidget(self.web)

        # Right hand side: Vertical layout for the tags
        vbox = QtGui.QVBoxLayout()
        if self.extracted_tags:
            for key, value in self.extracted_tags:
                tag = QtGui.QPushButton(key)
                tag.setMinimumSize(100, 40+5*value)
                tag.setCheckable(True)
                vbox.addWidget(tag)

        self.layout().addLayout(vbox)

        # Logging
        self.log.info("Finished UI init of %s" % self.__class__.__name__)

    def set_webpage(self, page):
        self.web.load(QtCore.QUrl(page))

    def loadNotebook(self, notebook, tags=[]):
        # Check the SHA1 sum to see if it has been computed already TODO
        # If not, compute it, recovering the list of tags, of dates TODO, and
        # the straight markdown file
        self.initLogic()
        self.log.info("Extracting markdown from %s" % notebook)
        markdown, tags = tp.from_notes_to_markdown(
            os.path.join(self.info.level, notebook))

        self.extracted_tags = tags
        # save a temp
        with open(os.path.join(self.website_root, notebook), 'w') as temp:
            temp.write('\n'.join(markdown))

        # Apply pandoc to this markdown file, from pypandoc thin wrapper, and
        # recover the html
        html = pa.convert(os.path.join(self.website_root, notebook), 'html')

        # Write the html to a file
        url = os.path.join(self.website_root, notebook.replace(
            EXTENSION, '.html'))
        with open(url, 'w') as page:
            page.write(html)
        # Finally, set the url of the web viewer to the desired page
        self.clearUI(2)
        self.initUI()
        self.set_webpage(url)

if __name__ == "__main__":
    application = QtGui.QApplication(sys.argv)
    example = ExampleFrame()
    sys.exit(application.exec_())
