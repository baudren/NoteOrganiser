from __future__ import unicode_literals
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class ModifiedMarkdownHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent=None):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        # Initialise the highlighting rules
        self.highlightingRules = []
        self.underliningRules = []

        # Date rules
        dateFormat = QtGui.QTextCharFormat()
        dateFormat.setForeground(QtCore.Qt.darkGray)
        self.highlightingRules.append(
            (QtCore.QRegExp("\*{1,1}(\\d{1,2}/\\d{2,2}/\\d{4,4}\*{1,1}"),
             dateFormat))

        # Italics rules
        italicsFormat = QtGui.QTextCharFormat()
        italicsFormat.setFontItalic(True)
        italicsFormat.setForeground(QtCore.Qt.darkGreen)
        self.highlightingRules.append(
            (QtCore.QRegExp("\*{1,1}([^\n^\*]+)\*{1,1}"), italicsFormat))

        # Bold rules
        boldFormat = QtGui.QTextCharFormat()
        boldFormat.setForeground(QtCore.Qt.darkBlue)
        boldFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightingRules.append(
            (QtCore.QRegExp("\*{2,2}([^\n^\*]+)\*{2,2}"), boldFormat))

        # Code rules
        self.codeFormat = QtGui.QTextCharFormat()
        self.codeFormat.setForeground(QtCore.Qt.darkBlue)
        self.highlightingRules.append(
            (QtCore.QRegExp("`{1,1}([^\n^`]+)`{1,1}"), self.codeFormat))

        # Tags
        tagFormat = QtGui.QTextCharFormat()
        tagFormat.setForeground(QtCore.Qt.darkRed)
        self.highlightingRules.append(
            (QtCore.QRegExp(
                "^# ((\w(?:[-\w]*\w)?)+)(,\s*(\w(?:[-\w]*\w)?)+)*$"),
                tagFormat))

        # Code blocks (several lines)
        self.blockStartExpression = QtCore.QRegExp("^~~~(\s.*)?$")
        self.blockEndExpression = QtCore.QRegExp("^~~~$")

        # Main title rule
        self.mainTitleUnderlineExpression = QtCore.QRegExp("^={2,}$")
        mainTitleFormat = QtGui.QTextCharFormat()
        mainTitleFormat.setForeground(QtCore.Qt.darkGreen)
        # Sections rule
        self.sectionUnderlineExpression = QtCore.QRegExp("^-{2,}$")
        sectionFormat = QtGui.QTextCharFormat()
        sectionFormat.setForeground(QtCore.Qt.darkBlue)
        self.underliningRules.extend(
            [(self.mainTitleUnderlineExpression, mainTitleFormat),
             (self.sectionUnderlineExpression, sectionFormat)])

    def highlightBlock(self, text):
        # Deal first with simple expressions (one line)
        # Note: the _format syntax is there to avoid naming conflict with the
        # restricted word `format`.
        for pattern, _format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, _format)
                index = expression.indexIn(text, index + length)

        # Deal with block type highlighting
        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.blockStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.blockEndExpression.indexIn(
                text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                blockLength = len(text) - startIndex
            elif endIndex == 0:
                # This is a symmetric code block
                if self.previousBlockState() == 0:
                    self.setCurrentBlockState(1)
                blockLength = len(text) - startIndex
            else:
                blockLength = endIndex - startIndex + \
                    self.blockEndExpression.matchedLength()

            self.setFormat(startIndex, blockLength,
                           self.codeFormat)
            startIndex = self.blockStartExpression.indexIn(
                text, startIndex + blockLength)

        # Match the underlines
        if startIndex == -1:  # If outside of a block
            if self.previousBlockState() != 2:
                for pattern, _format in self.underliningRules:
                    expression = QtCore.QRegExp(pattern)
                    # Match the next line for underlines
                    index = expression.indexIn(
                        self.currentBlock().next().text())
                    if index >= 0:
                        length = expression.matchedLength()
                        self.setFormat(index, length, _format)
                        index = expression.indexIn(text, index + length)
                        self.setCurrentBlockState(2)
            # If the title has already been highlighted, the state is '2'
            else:
                for pattern, _format in self.underliningRules:
                    expression = QtCore.QRegExp(pattern)
                    # Match the next line for underlines
                    index = expression.indexIn(text)
                    if index >= 0:
                        length = expression.matchedLength()
                        self.setFormat(index, length, _format)
                        index = expression.indexIn(text, index + length)
