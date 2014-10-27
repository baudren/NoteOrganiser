import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class ModifiedMarkdownHighlighter(QtGui.QSyntaxHighlighter):

    def highlightBlock(self, text):
        classFormat = QtGui.QTextCharFormat()
        classFormat.setFontWeight(QtGui.QFont.Bold)
        classFormat.setForeground(QtCore.Qt.darkMagenta)
        pattern = u"\\bMy[A-Za-z]+\\b"

        expression = QtCore.QRegExp(pattern)
        index = text.indexOf(expression)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, classFormat)
            index = text.indexOf(expression, index + length)
