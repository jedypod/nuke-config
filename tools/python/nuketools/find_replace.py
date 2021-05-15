from __future__ import absolute_import
import nuke
import nukescripts
import re

if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
else:
    from PySide2 import QtWidgets, QtGui, QtCore


nuke.menu('Nuke').addCommand('Edit/Node/Filename/Find Replace', 'find_replace.show()', 'ctrl+/')


class FindReplace(QtWidgets.QDialog):
    def __init__(self, parent):
        super(FindReplace, self).__init__(parent)

        self.knob_matches = dict() # knob matches: { <knob>: [<node>, new_knobval] }

        # Get candidate nodes
        nodes = nuke.selectedNodes()
        if nodes:
            self.node_candidates = nodes
        else:
            self.node_candidates = nuke.allNodes(recurseGroups=True)

        self._setup_ui()


    def _setup_ui(self):
        ''' Build UI
        '''

        self.setWindowTitle('Find Replace')

        master_layout = QtWidgets.QGridLayout()
        self.setLayout(master_layout)


        # Find Layout
        layout_find = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText('find')
        self.find_text = QtWidgets.QLineEdit()

        self.chkbx_regex = QtWidgets.QCheckBox('.*')
        self.chkbx_regex.setChecked(True)
        self.chkbx_regex.setToolTip('Enable Regular Expressions in search')
        self.chkbx_case_sensitive = QtWidgets.QCheckBox('Aa')
        self.chkbx_case_sensitive.setChecked(True)
        self.chkbx_case_sensitive.setToolTip('Enable case sensitive searching')
        self.find_button = QtWidgets.QPushButton('find')


        master_layout.addWidget(label, 0, 0)
        layout_find.addWidget(self.find_text)
        layout_find.addWidget(self.chkbx_regex)
        layout_find.addWidget(self.chkbx_case_sensitive)
        layout_find.addWidget(self.find_button)
        master_layout.addLayout(layout_find, 0, 1)


        # Replace layout
        layout_replace = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        label.setText('replace')
        self.replace_text = QtWidgets.QLineEdit()
        self.replace_button = QtWidgets.QPushButton('replace')
        master_layout.addWidget(label, 1, 0)
        layout_replace.addWidget(self.replace_text)
        layout_replace.addWidget(self.replace_button)
        master_layout.addLayout(layout_replace, 1, 1)


        # # Find Options
        # self.combo_knobs = QtWidgets.QComboBox()
        # self.combo_knobs.addItems(['File_Knob', 'Eval_String_Knob', 'Multiline_Eval_String_Knob', ])
        # layout_find.addWidget(self.combo_knobs)
        # layout_options = QtWidgets.QHBoxLayout()
        # master_layout.addLayout(layout_options, 3, 1)

        # Info panel
        label = QtWidgets.QLabel()
        label.setText('info')
        self.infobox = QtWidgets.QPlainTextEdit()
        self.infobox.setReadOnly(True)
        self.infobox.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        master_layout.addWidget(label, 4, 0)
        master_layout.addWidget(self.infobox, 4, 1)
        self.resize(1000, 400)

        # Connect signals
        self.find_button.clicked.connect(self.find_knobs)
        self.replace_button.clicked.connect(self.replace_knobs)
        self.find_text.textChanged.connect(self.find_knobs)
        self.replace_text.textChanged.connect(self.find_knobs)
        self.chkbx_regex.clicked.connect(self.find_knobs)
        self.chkbx_case_sensitive.clicked.connect(self.find_knobs)


    def find_knobs(self):
        ''' Search all candidate nodes for candidate knobs and populate self.knob_matches
        '''
       
        # Reset knob matches
        self.knob_matches = dict()

        # Enabled knob classes
        knob_classes = ['File_Knob', 'Eval_String_Knob', 'Multiline_Eval_String_Knob', ]
        
        # Knob name blacklist
        knob_blacklist = ['icon']


        # Gather info
        search_pattern = self.find_text.text()
        replace_pattern = self.replace_text.text()
        regex = self.chkbx_regex.checkState()
        case_sensitive = self.chkbx_case_sensitive.checkState()
        
        # Compile regex search patterns
        if not regex:
            search_pattern = re.escape(search_pattern)
        
        if case_sensitive:
            pattern = re.compile(search_pattern)
        else:
            pattern = re.compile(search_pattern, re.IGNORECASE)

        if not search_pattern:
            self.knob_matches = dict()
            self.populate_info()
            return

        # knob_class = self.combo_knobs.currentText()

        _ = [n.setSelected(False) for n in nuke.allNodes(recurseGroups=True)]


        for node in self.node_candidates:
            for k in node.knobs():
                if node[k].Class() in knob_classes and k not in knob_blacklist:
                    knobval = node[k].getValue()
                    match = pattern.search(knobval)
                    if match:
                        if not replace_pattern:
                            new_knobval = ''
                        else:
                            if regex:
                                new_knobval = pattern.sub(replace_pattern, knobval)
                            else:
                                new_knobval = knobval.replace(search_pattern, replace_pattern)

                        self.knob_matches[node[k]] = [node, new_knobval]
                        node.setSelected(True)
        
        self.populate_info()


    def populate_info(self):
        ''' Populate the info panel with the current search results and replace behavior
        '''
        if not self.knob_matches:
            infotext = 'no results'
            self.infobox.setPlainText(infotext)
            return

        sorted_knob_matches = sorted(list(self.knob_matches.items()), key=lambda k_v: k_v[1][0].fullName())

        infotext = ''
        for item in sorted_knob_matches:
            infotext += '{0}.{1}: \t{2}'.format(item[1][0].fullName(), item[0].name(), item[0].getValue())
            if item[1][1]:
                infotext += '\n-->\t{0}'.format(item[1][1])
            infotext += '\n'

        self.infobox.setPlainText(infotext)


    def replace_knobs(self):
        ''' Replace knob_matches with replace string
        '''
        if not self.knob_matches or not self.replace_text.text():
            return
        nuke.Undo().begin()
        for knob, val in list(self.knob_matches.items()):
            knob.setValue(val[1])
        nuke.Undo().end()
        self.find_knobs()


    def keyPressEvent(self, event):
        ''' Handle keyboard events.
            enter = search
            ctrl+enter = replace
        '''
        key = event.key()
        ctrl = bool(event.modifiers() & QtCore.Qt.ControlModifier)
        if key == QtCore.Qt.Key_Escape:
            self.quit()
        if (key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter):
            self.find_knobs()
        if (key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter) and ctrl:
            self.replace_knobs()


    def quit(self):
        self.close()


def show():
    panel = FindReplace(QtWidgets.QApplication.activeWindow())
    panel.show()
