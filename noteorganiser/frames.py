import sys
import os
import pypandoc as pa

from PySide import QtGui
from PySide import QtCore
from PySide import QtWebKit

from widgets import Shelves, NewEntry
from text_processing import from_notes_to_markdown
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
        # Create a shortcut notation for the list of notebooks
        self.parent = parent
        self.logger = parent.logger
        self.notebooks = self.parentWidget().notebooks
        self.folders = self.parentWidget().folders
        self.root = self.parentWidget().root

        if hasattr(self, 'initLogic'):
            self.initLogic()

        self.initUI()

    def initUI(self):
        raise NotImplementedError


class Library(CustomFrame):
    """
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
        self.logger.info("Starting UI init of %s" % self.__class__.__name__)
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        newNotebookButton = QtGui.QPushButton("&New Notebook")
        newNotebookButton.clicked.connect(self.parentWidget().create_notebook)

        newFolderButton = QtGui.QPushButton("New &Folder")
        newFolderButton.clicked.connect(self.parentWidget().create_folder)

        removeButton = QtGui.QPushButton("&Remove")
        self.shelves = Shelves(self.notebooks, self.folders, self)

        grid.addWidget(self.shelves, 0, 0, 5, 5)
        grid.addWidget(newNotebookButton, 1, 5)
        grid.addWidget(newFolderButton, 2, 5)
        grid.addWidget(removeButton, 3, 5)
        self.setLayout(grid)

        self.logger.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        self.shelves.add_notebook()


class Editing(CustomFrame):
    """
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
    |   N|                         | [-] delete       |
    |   1|                         |                  |
    |   \|_________________________|                  |
    ---------------------------------------------------
    """
    def initUI(self):
        self.logger.info("Starting UI init of %s" % self.__class__.__name__)
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(10)

        newButton = QtGui.QPushButton("&New entry", self)
        newButton.clicked.connect(self.newEntry)

        removeButton = QtGui.QPushButton("&Cancel", self)

        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabPosition(QtGui.QTabWidget.West)

        for notebook in self.notebooks:
            text = QtGui.QTextEdit(self.tabs)
            source = open(os.path.join(self.root, notebook)).read()
            text.setText(source)
            text.setTabChangesFocus(True)
            self.tabs.addTab(text, notebook.strip(EXTENSION))

        vbox = QtGui.QVBoxLayout()

        vbox.addWidget(newButton)
        vbox.addWidget(removeButton)

        self.grid.addWidget(self.tabs, 0, 0)
        self.grid.addLayout(vbox, 0, 1)

        self.setLayout(self.grid)
        self.logger.info("Finished UI init of %s" % self.__class__.__name__)

    def refresh(self):
        """Adding files"""
        new = self.notebooks[-1]
        text = QtGui.QTextEdit(self.tabs)
        source = open(os.path.join(self.root, new)).read()
        text.setText(source)
        text.setTabChangesFocus(True)
        self.tabs.addTab(text, new.strip(EXTENSION))
        self.grid.removeWidget(self.tabs)
        self.grid.addWidget(self.tabs, 0, 0)

    def switchNotebook(self, notebook):
        """switching tab to desired notebook"""
        self.parent.logger.info("switching to "+notebook)
        index = self.notebooks.index(notebook+EXTENSION)
        self.tabs.setCurrentIndex(index)

    def newEntry(self):
        """Open a form and store the results to the file"""
        self.popup = NewEntry(self)
        ok = self.popup.exec_()
        if ok:
            print self.popup


class Preview(CustomFrame):
    """
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
    def __init__(self, *args):
        CustomFrame.__init__(self, *args)

    def initLogic(self):
        self.website_root = os.path.join(self.root, 'website')
        self.sha = []

    def initUI(self):
        self.logger.info("Starting UI init of %s" % self.__class__.__name__)
        self.hbox = QtGui.QHBoxLayout()

        # Left hand side: html window
        self.web = QtWebKit.QWebView(self)
        # Set the css file. Note that the path to the css needs to be absolute,
        # somehow...
        local_path = os.getcwd()
        self.web.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile(
            os.path.join(local_path, 'noteorganiser', 'assets', 'style',
                         'default.css')))

        # temp
        self.load_notebook("python.md")

        self.hbox.addWidget(self.web)

        # Right hand side: Vertical layout
        self.vbox = QtGui.QVBoxLayout()
        self.hbox.addLayout(self.vbox)

        # Set the global layout
        self.setLayout(self.hbox)
        # Logging
        self.logger.info("Finished UI init of %s" % self.__class__.__name__)

    def set_webpage(self, page):
        self.web.load(QtCore.QUrl(page))

    def load_notebook(self, notebook, tags=[]):
        # Check the SHA1 sum to see if it has been computed already TODO
        # If not, compute it, recovering the list of tags, of dates TODO, and
        # the straight markdown file
        markdown, extracted_tags = from_notes_to_markdown(
            os.path.join(self.root, notebook))

        # save a temp
        with open(os.path.join(self.website_root, notebook), 'w') as temp:
            temp.write('\n'.join(markdown))

        # Apply pandoc to this markdown file, from pypandoc thin wrapper, and
        # recover the html
        #html = pa.convert('\n'.join(markdown), 'html', format='markdown')
        html = pa.convert(os.path.join(self.website_root, notebook), 'html')

        # Write the html to a file
        url = os.path.join(self.website_root, notebook.replace(
            EXTENSION, '.html'))
        with open(url, 'w') as page:
            page.write(html)
        # Finally, set the url of the web viewer to the desired page
        self.set_webpage(url)

if __name__ == "__main__":
    application = QtGui.QApplication(sys.argv)
    example = ExampleFrame()
    sys.exit(application.exec_())
