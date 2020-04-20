import nuke

# from Qt import QtCore, QtWidgets, QtGui

if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
    from PySide.QtCore import Qt
else:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Qt


from QtUtils import CodeTextEdit


nuke.menu('Nuke').addCommand('Edit/Node/Set Label', 'labeler.label()', 'shift+a')


class LabelPanel(QtWidgets.QWidget):
    ''' Show a text entry interface for entering text for a node label
    '''
    def __init__(self, nodes, _parent=None):
        super(LabelPanel, self).__init__()
        
        if not nodes:
            return
        self.nodes = nodes
        self.setup_ui()

    def setup_ui(self):
        ''' Set up the user interface
        '''
        container = QtWidgets.QVBoxLayout()

        # self.text = QtWidgets.QPlainTextEdit()
        self.text = CodeTextEdit() # Use our souped-up code editor widget from Knob Scripter
        container.addWidget(self.text)
        
        # Create Ok / Cancel buttons
        ok_button = QtWidgets.QPushButton('Ok')
        ok_button.clicked.connect(self.set_label)
        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.clicked.connect(self.quit)
        
        # Create hbox widget for buttons
        buttonbox = QtWidgets.QHBoxLayout()
        buttonbox.addWidget(ok_button)
        buttonbox.addWidget(cancel_button)
        
        # Add button box to container
        container.addLayout(buttonbox)
        
        self.setLayout(container)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(QtCore.Qt.X11BypassWindowManagerHint)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(self.sizeHint().width(), self.sizeHint().height())
        
        # Populate text with existing label
        self.get_label()

        # Invoke window
        self.setWindowTitle('Set Label')
        self.under_cursor()
        self.show()

    def get_label(self):
        ''' Get label from last selected node. Populate the text field with it.
        ''' 
        label = self.nodes[0]['label'].getValue()
        if label:
            self.text.setPlainText(label)

    def set_label(self):
        ''' Set label of all nodes with user text
        '''
        label = self.text.document().toPlainText()
        for node in self.nodes:
            if node.Class() == 'Dot':
                if not label.startswith(' '):
                    label = ' ' + label
            node['label'].setValue(label)
        self.close()

    def under_cursor(self):
        def clamp(val, mini, maxi):
            return max(min(val, maxi), mini)
        # Get cursor position, and screen dimensions on active screen
        cursor = QtGui.QCursor().pos()
        screen = QtWidgets.QDesktopWidget().screenGeometry(cursor)
        # Get window position so cursor is just over text input
        xpos = cursor.x() - (self.width() / 2)
        ypos = cursor.y() - 13
        # Clamp window location to prevent it going offscreen
        xpos = clamp(xpos, screen.left(), screen.right() - self.width())
        ypos = clamp(ypos, screen.top(), screen.bottom() - (self.height() - 13))
        self.move(xpos, ypos)

    def keyPressEvent(self, event):
        '''Handle keyboard events.'''
        key = event.key()
        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        alt = bool(event.modifiers() & Qt.AltModifier)
        shift = bool(event.modifiers() & Qt.ShiftModifier)

        if key == QtCore.Qt.Key_Escape:
            self.close()
        
        if (key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter) and ctrl:
            self.set_label()

    def quit(self):
        self.close()


def label(nodes=None):
    ''' Prompt user for a new node label 
    '''
    if not nodes:
        nodes = nuke.selectedNodes()
    windows = [
        obj for obj in QtWidgets.QApplication.topLevelWidgets()
        if (obj.inherits('QMainWindow') and
        obj.metaObject().className() == 'Foundry::UI::DockMainWindow')
        ]
    if windows:
        nuke_main_window = windows[0]
    global panel
    panel = LabelPanel(nodes, _parent=nuke_main_window)


