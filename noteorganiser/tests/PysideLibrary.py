import os
import importlib
from robot.api import logger

from PySide import QtGui
from PySide import QtTest


class PysideLibrary:

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = '0.1'

    def open_application(self, module, name, *args, **kwargs):
        # Check if the module exists
        print 'trying to import %s.%s' % (module, name)

        module = importlib.import_module(module)
        definition = getattr(module, name)

        # Create the Qt Application
        application = QtGui.QApplication.instance()
        if application is None:
            application = QtGui.QApplication([])
        self.application = application

        # Instanciate
        self._main = definition(*args, **kwargs) 

        # wait for it to appear
        self.waitForWindowShown(self._main)

    def waitForWindowShown(self, widget):
        if hasattr(QtTest.QTest, 'qWaitForWindowShown'):
            # PyQt4
            QtTest.QTest.qWaitForWindowShown(widget)
        else:
            # PyQt5
            QtTest.QTest.qWaitForWindowExposed(widget)

    def close_application(self):
        self.application.exit()

    def screenCaptureWindow(self, name='screen', extension='png'):
        self.screenCaptureWidget(self._main, name, extension)

    def screenCaptureWidget(self, widget, name='screen', extension='png'):
        rfg = getRelativeFrameGeometry(widget)
        pixmap =  QtGui.QPixmap.grabWindow(widget.winId(),
                                        rfg.left(), rfg.top(),
                                        rfg.width(), rfg.height())
        pixmap.save(name, extension)


def getRelativeFrameGeometry(widget):
    g = widget.geometry()
    fg = widget.frameGeometry()
    return fg.translated(-g.left(),-g.top())

