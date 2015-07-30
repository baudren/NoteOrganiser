"""custom utilities"""

from __future__ import unicode_literals

from PySide import QtGui
from PySide import QtCore

import re


def fuzzySearch(searchInput, baseString):
    """fuzzy comparison of the strings"""
    #normalize strings
    searchInput = re.sub(r'\s', r' ', searchInput.lower())
    baseString = re.sub(r'\s', r' ', baseString.lower())

    #normal substring comparison
    if searchInput in baseString:
        return True

    # split searchInput and check them separately
    if ' ' in searchInput:
        if not [subString for subString in searchInput.split(' ') if not
                fuzzySearch(subString, baseString)]:
            return True

    # no match found
    return False


class MultiCompleter(QtGui.QCompleter):
    """
    Custom completer for multiple items

    This completer can be used in every text-widget
    The separator can be set with setSeparator.
    The standard separator is ','

    example to set it for a widget:
        tester = QtGui.QLineEdit
        tags = ['items', 'to', 'complete']
        completer = MultiCompleter(tags, self)
        tester.setCompleter(completer)
    """
    # separator for multi-item completion
    separators = [',', ';']

    def pathFromIndex(self, index):
        """
        add the completed string to the whole string

        this replaces the substring after the last instance of separator
        with the completed string
        """
        path = QtGui.QCompleter.pathFromIndex(self, index)

        oldText = str(self.widget().text())
        path = re.sub(r'[^{0}]*$'.format(''.join(self.separators)),
                      ' ' + path, oldText)

        return path

    def splitPath(self, path):
        """
        get the substring after the last instace of separator

        this substring is used for completion
        """
        path = re.sub('.*[{0}]\s*|\s*'.format(''.join(self.separators)),
                      '', path)
        return [path]

    def setSeparators(self, separators):
        """
        change the separators for multi-item completion

        the standard separators are [',', ';']
        """
        if separators:
            self.separators = separators


class FlowLayout(QtGui.QLayout):
    """
    PySide port of the layouts/flowlayout example from Qt v4.x
    The flowlayout automatically rearranges its items to fit horizontally

    this class is taken from the pyside examples:
    https://github.com/PySide/Examples/tree/master/examples/layouts
    """

    def __init__(self, parent=None, margin=0, spacing=-1):

        QtGui.QLayout.__init__(self, parent)

        if parent is not None:
            self.setMargin(margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        QtGui.QLayout.setGeometry(self, rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2*self.contentsMargins().top(),
                             2*self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            spaceX = self.spacing()
            spaceY = self.spacing()

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y),
                                 item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
