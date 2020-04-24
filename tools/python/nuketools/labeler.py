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


class LabelPanel(QtWidgets.QDialog):
    ''' Show a text entry interface for entering text for a node label
    '''
    def __init__(self, nodes, _parent=QtWidgets.QApplication.activeWindow()):
        super(LabelPanel, self).__init__(_parent)
        
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
        
        # Populate text with existing label
        self.get_label()

        # Invoke window
        self.setWindowTitle('Set Label')
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.setWindowFlags(QtCore.Qt.X11BypassWindowManagerHint)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(QtCore.Qt.Tool)
        self.setMinimumSize(self.sizeHint().width(), self.sizeHint().height())
        self.move(QtGui.QCursor().pos() - QtCore.QPoint(32,74))
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
            self.close()

        if ctrl and key == QtCore.Qt.Key_S:
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


