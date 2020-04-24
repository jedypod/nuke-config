import nuke


if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
else:
    from PySide2 import QtWidgets, QtGui, QtCore


from QtUtils import CodeTextEdit


nuke.menu('Nuke').addCommand('Edit/Node/Set Label', 'labeler.label(nodes=nuke.selectedNodes())', 'shift+a')


class LabelPanel(QtWidgets.QDialog):
    ''' Show a text entry interface for entering text for a node label
    '''
    def __init__(self, nodes, parent):
        super(LabelPanel, self).__init__(parent)
        
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
        ok_button.clicked.connect(self.set_and_quit)
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
        # self.setWindowFlags(QtCore.Qt.Tool) # This is not necessary for stay on top behavior in < Nuke12 if parent is passed on instantiation
        self.setMinimumSize(self.sizeHint().width(), self.sizeHint().height())
        self.move(QtGui.QCursor().pos() - QtCore.QPoint(32,74))
        # self.show()

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

    def set_and_quit(self):
        # Set label and close (for ok button)
        self.set_label()
        self.quit()
        

    def keyPressEvent(self, event):
        '''Handle keyboard events.'''
        key = event.key()
        ctrl = bool(event.modifiers() & QtCore.Qt.ControlModifier)
        alt = bool(event.modifiers() & QtCore.Qt.AltModifier)
        shift = bool(event.modifiers() & QtCore.Qt.ShiftModifier)

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
        return

    panel = LabelPanel(nodes, QtWidgets.QApplication.activeWindow())
    panel.show()