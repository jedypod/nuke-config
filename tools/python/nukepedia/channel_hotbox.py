"""
This module provides an Interface class to toggle and shuffle layer.

Channel Hotbox v1.6 for Nuke
by Falk Hofmann, London, 2013, last updated  may,2018
>> Updated with suggestion from Mitchell Kehn to better handle window focus.

This script allows you to switch, shuffle out or grade channels.

regular click:
Change the viewer to the selected channel.

shift+click:
Shuffle out all selected channels.

ctrl+click:
Create grade node with channel set to selected.

alt:
Switch viewer back to rgba.


falk@kombinat-13b.de

To install with hotkey on alt+q, add this to your menu.py and make sure that
the script is located in your nuke plugin path:

import channel_hotbox
nuke.menu("Nuke").findItem("Edit").addCommand("HotBox", 'channel_hotbox.start()', "alt+q")

"""

import math
import nuke  # pylint: disable=import-error



# Set up Menu
nuke.menu('Nuke').addCommand('Viewer/Channel Hotbox', 'channel_hotbox.start()', 'alt+meta+`')


try:
    # < Nuke 11
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    import PySide.QtGui as QtGuiWidgets
except ImportError:
    # >= Nuke 11
    import PySide2.QtCore as QtCore
    import PySide2.QtGui as QtGui
    import PySide2.QtWidgets as QtGuiWidgets


HOTBOX = None

COLORS = {'regular': "background-color:#282828; font: 13px",
          'orange': "background-color:#C26828; font: 13px",
          'green': "background-color: #1EB028; font: 13px"}


class LayerButton(QtGuiWidgets.QPushButton):
    """Custom QPushButton to change colors when hovering above."""
    def __init__(self, name, button_width, parent=None):
        super(LayerButton, self).__init__(parent)
        self.setMouseTracking(True)
        self.setText(name)
        self.setMinimumWidth(button_width / 2)
        self.setSizePolicy(QtGuiWidgets.QSizePolicy.Preferred,
                           QtGuiWidgets.QSizePolicy.Expanding)
        self.setStyleSheet(COLORS['regular'])

    def enterEvent(self, event):  # pylint: disable=invalid-name,unused-argument
        """Change color to orange when mouse enters button."""
        if not self.styleSheet() == COLORS['green']:
            self.setStyleSheet(COLORS['orange'])

    def leaveEvent(self, event):  # pylint: disable=invalid-name,unused-argument
        """Change color to grey when mouse leaves button."""
        if not self.styleSheet() == COLORS['green']:
            self.setStyleSheet(COLORS['regular'])


class LineEdit(QtGuiWidgets.QLineEdit):
    """Custom QLineEdit with combined auto completion."""
    def __init__(self, parent, layer_list):
        super(LineEdit, self).__init__(parent)
        self.parent = parent
        self.setSizePolicy(QtGuiWidgets.QSizePolicy.Preferred,
                           QtGuiWidgets.QSizePolicy.Expanding)
        self.completer = QtGuiWidgets.QCompleter(layer_list, self)
        self.completer.setCompletionMode(QtGuiWidgets.QCompleter.InlineCompletion)  # pylint: disable=line-too-long
        self.setCompleter(self.completer)
        self.completer.activated.connect(self.returnPressed)


class HotBox(QtGuiWidgets.QWidget):
    """User Interface class to provide buttons for each channel layer."""
    shuffle_list = []

    def __init__(self):
        super(HotBox, self).__init__()

        self.active_viewer = nuke.activeViewer().node()
        viewer = self.active_viewer.input(nuke.activeViewer().activeInput())

        layers = list(set([layers.split('.')[0] for layers in viewer.channels()]))
        layers.sort()

        if 'rgba' in layers:
            layers.remove('rgba')
            layers.insert(0, 'rgba')
            if 'rgb' in layers:
                layers.remove('rgb')
                layers.insert(1, 'rgb')
                if 'alpha' in layers:
                    layers.remove('alpha')
                    layers.insert(2, 'alpha')
            elif 'alpha' in layers:
                layers.remove('alpha')
                layers.insert(1, 'alpha')

        length = math.ceil(math.sqrt(len(layers) + 1))
        width, height = length * 200, length * 50
        self.setFixedSize(width, height)
        offset = QtCore.QPoint(width * 0.5, height * 0.5)
        self.move(QtGui.QCursor.pos() - offset)

        grid = QtGuiWidgets.QGridLayout()
        self.setLayout(grid)

        column_counter, row_counter = 0, 0
        button_width = width / length

        for layer in layers:
            button = LayerButton(layer, button_width)
            button.clicked.connect(self.clicked)
            grid.addWidget(button, row_counter, column_counter)

            if column_counter > length:
                row_counter += 1
                column_counter = 0

            else:
                column_counter += 1

        self.input = LineEdit(self, layers)
        grid.addWidget(self.input, row_counter, column_counter)
        self.input.returnPressed.connect(self.line_enter)

        self.set_window_properties()

    def set_window_properties(self):
        """Set window falgs and focused widget."""
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # make sure the widgets closes when it loses focus
        self.installEventFilter(self)
        self.input.setFocus()

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """Route key press event to certain behaviors.

        Args:
            event (QtGui.QEvent): PySide key press event.

        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_Alt:
            nuke.activeViewer().node()['channels'].setValue('rgba')
            self.close()

    def keyReleaseEvent(self, event):  # pylint: disable=invalid-name
        """Route key release event to certain behaviors.

        Args:
            event (QtGui.QEvent): PySide key release event.

        """
        if event.key() == QtCore.Qt.Key_Shift:
            if self.shuffle_list:
                nuke.activeViewer().node()['channels'].setValue('rgba')

                node = self.active_viewer.input(nuke.activeViewer().activeInput())
                for layer in self.shuffle_list:
                    shuffle = nuke.nodes.Shuffle(xpos=(node.xpos() + 100),
                                                 ypos=(node.ypos() + 50),
                                                 label='[value in]')
                    shuffle['in'].setValue(layer)
                    shuffle['selected'].setValue(True)
                    shuffle.setInput(0, node)
                    shuffle.autoplace()

                self.close()
            self.shuffle_list = []

    def clicked(self):
        """Route click events based on key modifier."""
        modifiers = QtGuiWidgets.QApplication.keyboardModifiers()

        if modifiers == QtCore.Qt.ShiftModifier:
            channel = self.sender().text()

            if channel in self.shuffle_list:
                self.shuffle_list.remove(channel)
                self.sender().setStyleSheet(COLORS['regular'])
            else:
                self.shuffle_list.append(channel)
                self.sender().setStyleSheet(COLORS['green'])

        elif modifiers == QtCore.Qt.ControlModifier:
            node = self.active_viewer.input(nuke.activeViewer().activeInput())
            self.close()
            node.setSelected(True)
            grade = nuke.createNode("Grade")
            grade['channels'].setValue(self.sender().text())

        else:
            self.active_viewer['channels'].setValue(self.sender().text())
            self.close()

    def line_enter(self):
        """Change Viewer to completed text."""
        self.active_viewer['channels'].setValue(self.input.text())
        self.close()

    def eventFilter(self, object, event):
        if event.type() in [QtCore.QEvent.WindowDeactivate, QtCore.QEvent.FocusOut]:
            self.close()
            return True
        return False


def start():
    """Start up function for Hotbox. Checks if Viewer available and active."""
    if nuke.allNodes('Viewer'):
        if nuke.activeViewer().activeInput() is not None:
            global HOTBOX  # pylint: disable=global-statement
            HOTBOX = HotBox()
            HOTBOX.show()
        else:
            print('No active viewer connected to node.')
    else:
        print('No viewer found in script.')