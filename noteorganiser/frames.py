import sys
from PySide import QtGui

from widgets import Shelves


class ExampleFrame(QtGui.QFrame):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        self.show()


class Library(QtGui.QFrame):
    """
    The notebooks will be stored and displayed there

    Should ressemble something like this:
     _________  _________  ____________
    / Library \/ Editing \/ Previewing \
    |          ----------------------------------
    |                              |            |
    |   notebook_1     notebook_2  | [+] new    |
    | ------------------------------ [-] delete |
    |                              |            |
    |   notebook_3                 |            |
    --------------------------------------------|
    """

    def __init__(self):
        """ Create the basic layout """
        QtGui.QFrame.__init__(self)

        self.initUI()

    def initUI(self):

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        newButton = QtGui.QPushButton("New")
        removeButton = QtGui.QPushButton("Remove")
        shelves = Shelves(['Research', 'Conferences'])

        grid.addWidget(shelves, 0, 0, 5, 5)
        grid.addWidget(newButton, 1, 5)
        grid.addWidget(removeButton, 2, 5)
        self.setLayout(grid)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    example = ExampleFrame()
    sys.exit(app.exec_())
