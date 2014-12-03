from __future__ import unicode_literals
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class ModifiedMarkdownHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent=None):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        # Initialise the highlighting rules
        self.highlightingRules = []

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
            (QtCore.QRegExp("\*{1,1}([^\n]+)\*{1,1}"), italicsFormat))

        # Bold rules
        boldFormat = QtGui.QTextCharFormat()
        boldFormat.setForeground(QtCore.Qt.darkBlue)
        boldFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightingRules.append(
            (QtCore.QRegExp("\*{2,2}([^\n]+)\*{2,2}"), boldFormat))

        # Tags
        tagFormat = QtGui.QTextCharFormat()
        # Main title rule
        self.mainTitleUnderlineExpression = QtCore.QRegExp("={3,}")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        #self.setCurrentBlockState(0)
        #startIndex = 0
        #if self.previousBlockState() != 1:
            #startIndex = self.commentStartExpression.indexIn(text)

        #while startIndex >= 0:
            #endIndex = self.commentEndExpression.indexIn(
                #text, startIndex)

            #if endIndex == -1:
                #self.setCurrentBlockState(1)
                #commentLength = text.length() - startIndex
            #else:
                #commentLength = endIndex - startIndex + \
                    #self.commentEndExpression.matchedLength()

            #self.setFormat(startIndex, commentLength,
                           #self.multiLineCommentFormat)
            #startIndex = self.commentStartExpression.indexIn(
                #text, startIndex + commentLength)


class Highlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, parent=None):

        super(Highlighter, self).__init__(parent)

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtCore.Qt.darkBlue)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywordPatterns = [
            "\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
            "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
            "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
            "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
            "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
            "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
            "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
            "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
            "\\bvolatile\\b"]

        self.highlightingRules = [
            (QtCore.QRegExp(pattern), keywordFormat)
            for pattern in keywordPatterns]

        classFormat = QtGui.QTextCharFormat()
        classFormat.setFontWeight(QtGui.QFont.Bold)
        classFormat.setForeground(QtCore.Qt.darkMagenta)
        self.highlightingRules.append(
            (QtCore.QRegExp("\\bQ[A-Za-z]+\\b"), classFormat))

        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtCore.Qt.red)
        self.highlightingRules.append(
            (QtCore.QRegExp("//[^\n]*"), singleLineCommentFormat))

        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QtCore.Qt.red)

        quotationFormat = QtGui.QTextCharFormat()
        quotationFormat.setForeground(QtCore.Qt.darkGreen)
        self.highlightingRules.append(
            (QtCore.QRegExp("\".*\""), quotationFormat))

        functionFormat = QtGui.QTextCharFormat()
        functionFormat.setFontItalic(True)
        functionFormat.setForeground(QtCore.Qt.blue)
        self.highlightingRules.append(
            (QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()"), functionFormat))

        self.commentStartExpression = QtCore.QRegExp("/\\*")
        self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(
                text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = text.length() - startIndex
            else:
                commentLength = endIndex - startIndex + \
                    self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                           self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(
                text, startIndex + commentLength)
