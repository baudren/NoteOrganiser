from robot.api.deco import keyword
from PySide.QtTest import QTest
import PySide.QtCore as QtCore

class LibraryKeywords(object):

    def library_tab_should_be_opened(self):
        # Get the tab widget
        tab = self._main.tabs
        assert tab.tabText(tab.currentIndex()).replace('&', '') == 'Library', \
                "expected 'Library', was %s" % tab.tabText(tab.currentIndex())

    @keyword('create a notebook named ${name}')
    def create_a_notebook_named(self, name):
        QTest.mouseClick(
            self._main.library.newNotebookAction, QtCore.Qt.LeftButton)

    @keyword('the notebook ${name} should be present')
    def the_notebook_should_be_present(self, name):
        raise NotImplementedError

    @keyword('the notebook ${name} should be absent')
    def the_notebook_should_be_absent(self, name):
        return not the_notebook_should_be_present()

    @keyword('remove notebook ${name}')
    def remove_notebook(self, name):
        raise NotImplementedError

    @keyword('create a folder named ${name}')
    def create_a_folder_named(self, name):
        raise NotImplementedError

    @keyword('the folder ${name} should be present')
    def the_folder_should_be_present(self, name):
        raise NotImplementedError

    @keyword('the folder ${name} should be absent')
    def the_folder_should_be_absent(self, name):
        return not the_folder_should_be_present()

    @keyword('remove folder ${name}')
    def remove_folder(self, name):
        raise NotImplementedError
