from __future__ import division

import nuke
import re

if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
    from PySide.QtCore import Qt
else:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Qt



# Code text edit widget
# Stolen directly from Adrian Pueyo's excellent KnobScripter

#------------------------------------------------------------------------------------------------------
# Script Editor Widget
# Wouter Gilsing built an incredibly useful python script editor for his Hotbox Manager, so I had it
# really easy for this part!
# Starting from his script editor, I changed the style and added the sublime-like functionality.
# I think this bit of code has the potential to get used in many nuke tools.
# Credit to him: http://www.woutergilsing.com/
# Originally used on W_Hotbox v1.5: http://www.nukepedia.com/python/ui/w_hotbox
#------------------------------------------------------------------------------------------------------

class CodeTextEdit(QtWidgets.QPlainTextEdit):
    # Signal that will be emitted when the user has changed the text
    userChangedEvent = QtCore.Signal()

    def __init__(self, knobScripter=""):
        super(CodeTextEdit, self).__init__()

        self.knobScripter = knobScripter
        self.selected_text = ""

        # Setup line numbers
        if self.knobScripter != "":
            self.tabSpaces = self.knobScripter.tabSpaces
        else:
            self.tabSpaces = 4
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth()

        # Highlight line
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.font = "Monospace"
        self.fontSize = 10

        self.editor_font = QtGui.QFont()
        self.editor_font.setFamily(self.font)
        self.editor_font.setStyleHint(QtGui.QFont.Monospace)
        self.editor_font.setFixedPitch(True)
        self.editor_font.setPointSize(self.fontSize)
        self.setFont(self.editor_font)

    #--------------------------------------------------------------------------------------------------
    # This is adapted from an original version by Wouter Gilsing.
    # Extract from his original comments:
    # While researching the implementation of line number, I had a look at Nuke's Blinkscript node. [..]
    # thefoundry.co.uk/products/nuke/developers/100/pythonreference/nukescripts.blinkscripteditor-pysrc.html
    # I stripped and modified the useful bits of the line number related parts of the code [..]
    # Credits to theFoundry for writing the blinkscripteditor, best example code I could wish for.
    #--------------------------------------------------------------------------------------------------

    def lineNumberAreaWidth(self):
        digits = 1
        maxNum = max(1, self.blockCount())
        while (maxNum >= 10):
            maxNum /= 10
            digits += 1

        space = 7 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):

        if (dy):
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if (rect.contains(self.viewport().rect())):
            self.updateLineNumberAreaWidth()

    def resizeEvent(self, event):
        QtWidgets.QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):

        if self.isReadOnly():
            return

        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor(36, 36, 36)) # Number bg


        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int( self.blockBoundingGeometry(block).translated(self.contentOffset()).top() )
        bottom = top + int( self.blockBoundingRect(block).height() )
        currentLine = self.document().findBlock(self.textCursor().position()).blockNumber()

        painter.setPen( self.palette().color(QtGui.QPalette.Text) )

        painterFont = QtGui.QFont()
        painterFont.setFamily("Courier")
        painterFont.setStyleHint(QtGui.QFont.Monospace)
        painterFont.setFixedPitch(True)
        if self.knobScripter != "":
            painterFont.setPointSize(self.knobScripter.fontSize)
            painter.setFont(self.knobScripter.script_editor_font)

        while (block.isValid() and top <= event.rect().bottom()):

            textColor = QtGui.QColor(110, 110, 110) # Numbers

            if blockNumber == currentLine and self.hasFocus():
                textColor = QtGui.QColor(255, 170, 0) # Number highlighted

            painter.setPen(textColor)

            number = "%s" % str(blockNumber + 1)
            painter.drawText(-3, top, self.lineNumberArea.width(), self.fontMetrics().height(), QtCore.Qt.AlignRight, number)

            # Move to the next block
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def keyPressEvent(self, event):
        '''
        Custom actions for specific keystrokes
        '''
        key = event.key()
        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        alt = bool(event.modifiers() & Qt.AltModifier)
        shift = bool(event.modifiers() & Qt.ShiftModifier)
        pre_scroll = self.verticalScrollBar().value()
        #modifiers = QtWidgets.QApplication.keyboardModifiers()
        #ctrl = (modifiers == Qt.ControlModifier)
        #shift = (modifiers == Qt.ShiftModifier)

        up_arrow = 16777235
        down_arrow = 16777237


        #if Tab convert to Space
        if key == 16777217:
            self.indentation('indent')

        #if Shift+Tab remove indent
        elif key == 16777218:
            self.indentation('unindent')

        #if BackSpace try to snap to previous indent level
        elif key == 16777219:
            if not self.unindentBackspace():
                QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
        else:
            ### COOL BEHAVIORS SIMILAR TO SUBLIME GO NEXT!
            cursor = self.textCursor()
            cpos = cursor.position()
            apos = cursor.anchor()
            text_before_cursor = self.toPlainText()[:min(cpos,apos)]
            text_after_cursor = self.toPlainText()[max(cpos,apos):]
            text_all = self.toPlainText()
            to_line_start = text_before_cursor[::-1].find("\n")
            if to_line_start == -1:
                linestart_pos = 0 # Position of the start of the line that includes the cursor selection start
            else:
                linestart_pos = len(text_before_cursor)-to_line_start

            to_line_end = text_after_cursor.find("\n")
            if to_line_end == -1:
                lineend_pos = len(text_all) # Position of the end of the line that includes the cursor selection end
            else:
                lineend_pos = max(cpos,apos)+to_line_end

            text_before_lines = text_all[:linestart_pos]
            text_after_lines = text_all[lineend_pos:]
            if len(text_after_lines) and text_after_lines.startswith("\n"):
                text_after_lines = text_after_lines[1:]
            text_lines = text_all[linestart_pos:lineend_pos]

            if cursor.hasSelection():
                selection = cursor.selection().toPlainText()
            else:
                selection = ""
            if key == Qt.Key_ParenLeft and (len(selection)>0 or re.match(r"[\s)}\];]+", text_after_cursor) or not len(text_after_cursor)): # (
                cursor.insertText("("+selection+")")
                cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif key == Qt.Key_ParenRight and text_after_cursor.startswith(")"): # )
                cursor.movePosition(QtGui.QTextCursor.NextCharacter)
                self.setTextCursor(cursor)
            elif key == Qt.Key_BracketLeft and (len(selection)>0 or re.match(r"[\s)}\];]+", text_after_cursor) or not len(text_after_cursor)): #[
                cursor.insertText("["+selection+"]")
                cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif key in [Qt.Key_BracketRight,43] and text_after_cursor.startswith("]"): # ]
                cursor.movePosition(QtGui.QTextCursor.NextCharacter)
                self.setTextCursor(cursor)
            elif key == Qt.Key_BraceLeft and (len(selection)>0 or re.match(r"[\s)}\];]+", text_after_cursor) or not len(text_after_cursor)): #{
                cursor.insertText("{"+selection+"}")
                cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif key in [199,Qt.Key_BraceRight] and text_after_cursor.startswith("}"): # }
                cursor.movePosition(QtGui.QTextCursor.NextCharacter)
                self.setTextCursor(cursor)
            elif key == 34: # "
                if len(selection)>0:
                    cursor.insertText('"'+selection+'"')
                    cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                elif text_after_cursor.startswith('"') and '"' in text_before_cursor.split("\n")[-1]:# and not re.search(r"(?:[\s)\]]+|$)",text_before_cursor):
                    cursor.movePosition(QtGui.QTextCursor.NextCharacter)
                elif not re.match(r"(?:[\s)\]]+|$)",text_after_cursor): # If chars after cursor, act normal
                    QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
                elif not re.search(r"[\s.({\[,]$", text_before_cursor) and text_before_cursor != "": # If chars before cursor, act normal
                    QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
                else:
                    cursor.insertText('"'+selection+'"')
                    cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif key == 39: # '
                if len(selection)>0:
                    cursor.insertText("'"+selection+"'")
                    cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                elif text_after_cursor.startswith("'") and "'" in text_before_cursor.split("\n")[-1]:# and not re.search(r"(?:[\s)\]]+|$)",text_before_cursor):
                    cursor.movePosition(QtGui.QTextCursor.NextCharacter)
                elif not re.match(r"(?:[\s)\]]+|$)",text_after_cursor): # If chars after cursor, act normal
                    QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
                elif not re.search(r"[\s.({\[,]$", text_before_cursor) and text_before_cursor != "": # If chars before cursor, act normal
                    QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
                else:
                    cursor.insertText("'"+selection+"'")
                    cursor.setPosition(apos+1, QtGui.QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos+1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
            elif key == 35 and len(selection): # # (yes, a hash)
                # If there's a selection, insert a hash at the start of each line.. how the fuck?
                if selection != "":
                    selection_split = selection.split("\n")
                    if all(i.startswith("#") for i in selection_split):
                        selection_commented = "\n".join([s[1:] for s in selection_split]) # Uncommented
                    else:
                        selection_commented = "#"+"\n#".join(selection_split)
                    cursor.insertText(selection_commented)
                    if apos > cpos:
                        cursor.setPosition(apos+len(selection_commented)-len(selection), QtGui.QTextCursor.MoveAnchor)
                        cursor.setPosition(cpos, QtGui.QTextCursor.KeepAnchor)
                    else:
                        cursor.setPosition(apos, QtGui.QTextCursor.MoveAnchor)
                        cursor.setPosition(cpos+len(selection_commented)-len(selection), QtGui.QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)

            elif key == 68 and ctrl and shift: #Ctrl+Shift+D, to duplicate text or line/s

                if not len(selection):
                    self.setPlainText(text_before_lines + text_lines+"\n"+text_lines+"\n" + text_after_lines)
                    cursor.setPosition(apos+len(text_lines)+1, QtGui.QTextCursor.MoveAnchor)
                    cursor.setPosition(cpos+len(text_lines)+1, QtGui.QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)
                    self.verticalScrollBar().setValue(pre_scroll)
                    self.scrollToCursor()
                else:
                    if text_before_cursor.endswith("\n") and not selection.startswith("\n"):
                        cursor.insertText(selection+"\n"+selection)
                        cursor.setPosition(apos+len(selection)+1, QtGui.QTextCursor.MoveAnchor)
                        cursor.setPosition(cpos+len(selection)+1, QtGui.QTextCursor.KeepAnchor)
                    else:
                        cursor.insertText(selection+selection)
                        cursor.setPosition(apos+len(selection), QtGui.QTextCursor.MoveAnchor)
                        cursor.setPosition(cpos+len(selection), QtGui.QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)

            elif key == up_arrow and ctrl and shift and len(text_before_lines): #Ctrl+Shift+Up, to move the selected line/s up
                prev_line_start_distance = text_before_lines[:-1][::-1].find("\n")
                if prev_line_start_distance == -1:
                    prev_line_start_pos = 0 #Position of the start of the previous line
                else:
                    prev_line_start_pos = len(text_before_lines)-1 - prev_line_start_distance
                prev_line = text_before_lines[prev_line_start_pos:]

                text_before_prev_line = text_before_lines[:prev_line_start_pos]

                if prev_line.endswith("\n"):
                    prev_line = prev_line[:-1]

                if len(text_after_lines):
                    text_after_lines = "\n"+text_after_lines

                self.setPlainText(text_before_prev_line + text_lines + "\n" + prev_line + text_after_lines)
                cursor.setPosition(apos-len(prev_line)-1, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(cpos-len(prev_line)-1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
                self.verticalScrollBar().setValue(pre_scroll)
                self.scrollToCursor()
                return

            elif key == down_arrow and ctrl and shift: #Ctrl+Shift+Up, to move the selected line/s up
                if not len(text_after_lines):
                    text_after_lines = ""
                next_line_end_distance = text_after_lines.find("\n")
                if next_line_end_distance == -1:
                    next_line_end_pos = len(text_all)
                else:
                    next_line_end_pos = next_line_end_distance
                next_line = text_after_lines[:next_line_end_pos]
                text_after_next_line = text_after_lines[next_line_end_pos:]

                self.setPlainText(text_before_lines + next_line + "\n" + text_lines + text_after_next_line)
                cursor.setPosition(apos+len(next_line)+1, QtGui.QTextCursor.MoveAnchor)
                cursor.setPosition(cpos+len(next_line)+1, QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
                self.verticalScrollBar().setValue(pre_scroll)
                self.scrollToCursor()
                return

            elif key == up_arrow and not len(text_before_lines): # If up key and nothing happens, go to start
                if not shift:
                    cursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
                    self.setTextCursor(cursor)
                else:
                    cursor.setPosition(0, QtGui.QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)

            elif key == down_arrow and not len(text_after_lines): # If up key and nothing happens, go to start
                if not shift:
                    cursor.setPosition(len(text_all), QtGui.QTextCursor.MoveAnchor)
                    self.setTextCursor(cursor)
                else:
                    cursor.setPosition(len(text_all), QtGui.QTextCursor.KeepAnchor)
                    self.setTextCursor(cursor)

            # If enter or return, match indent level. 
            # Ignore if Ctrl is pressed. This will be used for other stuff
            elif (key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter) and not ctrl:
                self.indentNewLine()
            else:
                QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

        self.scrollToCursor()

    def scrollToCursor(self):
        self.cursor = self.textCursor()
        self.cursor.movePosition(QtGui.QTextCursor.NoMove) # Does nothing, but makes the scroll go to the right place...
        self.setTextCursor(self.cursor)

    def getCursorInfo(self):

        self.cursor = self.textCursor()

        self.firstChar =  self.cursor.selectionStart()
        self.lastChar =  self.cursor.selectionEnd()

        self.noSelection = False
        if self.firstChar == self.lastChar:
            self.noSelection = True

        self.originalPosition = self.cursor.position()
        self.cursorBlockPos = self.cursor.positionInBlock()

    def unindentBackspace(self):
        '''
        #snap to previous indent level
        '''
        self.getCursorInfo()

        if not self.noSelection or self.cursorBlockPos == 0:
            return False

        #check text in front of cursor
        textInFront = self.document().findBlock(self.firstChar).text()[:self.cursorBlockPos]

        #check whether solely spaces
        if textInFront != ' '*self.cursorBlockPos:
            return False

        #snap to previous indent level
        spaces = len(textInFront)
        for space in range(spaces - ((spaces -1) /self.tabSpaces) * self.tabSpaces -1):
            self.cursor.deletePreviousChar()

    def indentNewLine(self):

        #in case selection covers multiple line, make it one line first
        self.insertPlainText('')

        self.getCursorInfo()

        #check how many spaces after cursor
        text = self.document().findBlock(self.firstChar).text()

        textInFront = text[:self.cursorBlockPos]

        if len(textInFront) == 0:
            self.insertPlainText('\n')
            return

        indentLevel = 0
        for i in textInFront:
            if i == ' ':
                indentLevel += 1
            else:
                break

        indentLevel /= self.tabSpaces

        #find out whether textInFront's last character was a ':'
        #if that's the case add another indent.
        #ignore any spaces at the end, however also
        #make sure textInFront is not just an indent
        if textInFront.count(' ') != len(textInFront):
            while textInFront[-1] == ' ':
                textInFront = textInFront[:-1]

        if textInFront[-1] == ':':
            indentLevel += 1

        #new line
        self.insertPlainText('\n')
        #match indent
        self.insertPlainText(' '*(self.tabSpaces*indentLevel))

    def indentation(self, mode):

        pre_scroll = self.verticalScrollBar().value()
        self.getCursorInfo()

        #if nothing is selected and mode is set to indent, simply insert as many
        #space as needed to reach the next indentation level.
        if self.noSelection and mode == 'indent':

            remainingSpaces = self.tabSpaces - (self.cursorBlockPos%self.tabSpaces)
            self.insertPlainText(' '*remainingSpaces)
            return

        selectedBlocks = self.findBlocks(self.firstChar, self.lastChar)
        beforeBlocks = self.findBlocks(last = self.firstChar -1, exclude = selectedBlocks)
        afterBlocks = self.findBlocks(first = self.lastChar + 1, exclude = selectedBlocks)

        beforeBlocksText = self.blocks2list(beforeBlocks)
        selectedBlocksText = self.blocks2list(selectedBlocks, mode)
        afterBlocksText = self.blocks2list(afterBlocks)

        combinedText = '\n'.join(beforeBlocksText + selectedBlocksText + afterBlocksText)

        #make sure the line count stays the same
        originalBlockCount = len(self.toPlainText().split('\n'))
        combinedText = '\n'.join(combinedText.split('\n')[:originalBlockCount])

        self.clear()
        self.setPlainText(combinedText)

        if self.noSelection:
            self.cursor.setPosition(self.lastChar)

        #check whether the the orignal selection was from top to bottom or vice versa
        else:
            if self.originalPosition == self.firstChar:
                first = self.lastChar
                last = self.firstChar
                firstBlockSnap = QtGui.QTextCursor.EndOfBlock
                lastBlockSnap = QtGui.QTextCursor.StartOfBlock
            else:
                first = self.firstChar
                last = self.lastChar
                firstBlockSnap = QtGui.QTextCursor.StartOfBlock
                lastBlockSnap = QtGui.QTextCursor.EndOfBlock

            self.cursor.setPosition(first)
            self.cursor.movePosition(firstBlockSnap,QtGui.QTextCursor.MoveAnchor)
            self.cursor.setPosition(last,QtGui.QTextCursor.KeepAnchor)
            self.cursor.movePosition(lastBlockSnap,QtGui.QTextCursor.KeepAnchor)

        self.setTextCursor(self.cursor)
        self.verticalScrollBar().setValue(pre_scroll)

    def findBlocks(self, first = 0, last = None, exclude = []):
        blocks = []
        if last == None:
            last = self.document().characterCount()
        for pos in range(first,last+1):
            block = self.document().findBlock(pos)
            if block not in blocks and block not in exclude:
                blocks.append(block)
        return blocks

    def blocks2list(self, blocks, mode = None):
        text = []
        for block in blocks:
            blockText = block.text()
            if mode == 'unindent':
                if blockText.startswith(' '*self.tabSpaces):
                    blockText = blockText[self.tabSpaces:]
                    self.lastChar -= self.tabSpaces
                elif blockText.startswith('\t'):
                    blockText = blockText[1:]
                    self.lastChar -= 1

            elif mode == 'indent':
                blockText = ' '*self.tabSpaces + blockText
                self.lastChar += self.tabSpaces

            text.append(blockText)

        return text

    def highlightCurrentLine(self):
        '''
        Highlight currently selected line
        '''
        extraSelections = []

        selection = QtWidgets.QTextEdit.ExtraSelection()

        lineColor = QtGui.QColor(62, 62, 62, 255)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()

        extraSelections.append(selection)

        self.setExtraSelections(extraSelections)
        self.scrollToCursor()

    def format(self,rgb, style=''):
        '''
        Return a QtWidgets.QTextCharFormat with the given attributes.
        '''
        color = QtGui.QColor(*rgb)
        textFormat = QtGui.QTextCharFormat()
        textFormat.setForeground(color)

        if 'bold' in style:
            textFormat.setFontWeight(QtGui.QFont.Bold)
        if 'italic' in style:
            textFormat.setFontItalic(True)
        if 'underline' in style:
            textFormat.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)

        return textFormat


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, scriptEditor):
        super(LineNumberArea, self).__init__(scriptEditor)

        self.scriptEditor = scriptEditor
        self.setStyleSheet("text-align: center;")

    def paintEvent(self, event):
        self.scriptEditor.lineNumberAreaPaintEvent(event)
        return


def _nuke_main_window():
    """Returns Nuke's main window"""
    # for obj in QtGui.qApp.topLevelWidgets():
    #     if (obj.inherits('QMainWindow') and obj.metaObject().className() == 'Foundry::UI::DockMainWindow'):
    #         return obj
    # else:
    #     raise RuntimeError('Could not find DockMainWindow instance')
    return QtWidgets.QApplication.activeWindow()
