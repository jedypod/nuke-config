from __future__ import print_function

"""
This module provides an Interface class to toggle and shuffle layer.

Channel Hotbox v2.0 for Nuke
by Falk Hofmann, London:2013, last updated  april, Berlin:2021

>>> Updated to work within Nuke 13/Python3, Shuffle2 bugfixes and case insensitivity user input.
>>> Updated to clear shuffle list properly to avoid storing layer in list after closing Hotbox.
>>> Updated to choose the creation of the new shuffle node.
>>> Updated with suggestion from Mitchell Kehn to better handle window focus.

This script allows you to switch the viewer channel or create shuffle and grade nodes.

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



__version__ = 2.0

import math
import nuke

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

# To create the new introduced Shuffle2 nodes in Nuke 12, set SHUFFLE_TYPE value to 1.
# SHUFFLE_TYPE = 0  old shuffle node
# SHUFFLE_TYPE = 1 new shuffle node

SHUFFLE_TYPE = 1


STYLESHEET = """
QPushButton[color="regular"]{background-color:#282828; font: 13px;}
QPushButton[color="regular"]:hover{background-color:#C26828; font: 13px;}
QPushButton[color="blue_hover"]{ background-color:#282828; font: 13px;}
QPushButton[color="blue_hover"]:hover{ background-color:#282828; font: 13px;
                                       border-style: solid; border-width: 3px;
                                       border-color: #8299C8;
                                       }
QPushButton[color="purple_hover"]{ background-color:#282828; font: 13px;}
QPushButton[color="purple_hover"]:hover{ Background-color:#282828; font: 13px;
                                         border-style: solid;
                                         border-width: 3px;
                                         border-color: #8F345D;
                                         }
QPushButton[color="blue_click"]{background-color:#8299C8; font: 13px;}
QPushButton[color="purple_click"]{background-color:#8F345D; font: 13px;}
"""


class LayerButton(QtGuiWidgets.QPushButton):
    """Custom QPushButton to change colors when hovering above."""

    def __init__(self, name, button_width, parent=None):
        super(LayerButton, self).__init__(parent)
        self.setMouseTracking(True)
        self.setText(name)
        self.setMinimumWidth(button_width / 2)
        self.setSizePolicy(QtGuiWidgets.QSizePolicy.Preferred,
                           QtGuiWidgets.QSizePolicy.Expanding)
        self.setStyleSheet(STYLESHEET)
        self.setProperty("color", "regular")


class LineEdit(QtGuiWidgets.QLineEdit):
    """Custom QLineEdit with combined auto completion."""

    def __init__(self, parent, layer_list):
        super(LineEdit, self).__init__(parent)
        self.parent = parent
        self.setSizePolicy(QtGuiWidgets.QSizePolicy.Preferred,
                           QtGuiWidgets.QSizePolicy.Expanding)
        self.completer = QtGuiWidgets.QCompleter(layer_list, self)
        self.completer.setCompletionMode(QtGuiWidgets.QCompleter.InlineCompletion)  # pylint: disable=line-too-long
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)  # pylint: disable=line-too-long
        self.setCompleter(self.completer)
        self.completer.activated.connect(self.returnPressed)


class HotBox(QtGuiWidgets.QWidget):
    """User Interface class to provide buttons for each channel layer."""

    def __init__(self):
        super(HotBox, self).__init__()
        self.shuffle_list = []
        self._buttons = []

        self.active_viewer = nuke.activeViewer().node()
        viewer = self.active_viewer.input(nuke.activeViewer().activeInput())

        layers = list(set([layers.split('.')[0] for layers in viewer.channels()]))
        layers.sort()
        self._channels = {layer.lower(): layer for layer in layers}
        self._channels["alpha"] = "alpha"

        if 'rgba' in layers:
            layers.remove('rgba')
            layers.insert(0, 'rgba')
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
            self._buttons.append(button)
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
        elif event.key() == QtCore.Qt.Key_Shift:
            self._update_styles("purple_hover")
        elif event.key() == QtCore.Qt.Key_Control:
            self._update_styles("blue_hover")

    def _update_styles(self, style):
        """Update property for stylesheet.

        Args:
            style (str): Color attribute for stylesheet.

        """
        for button in self._buttons:
            button.setProperty("color", style)
            button.setStyle(button.style())

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
                    nuke_version = int("{}{}".format(nuke.env.get("NukeVersionMajor"),
                                                     nuke.env.get("NukeVersionMinor")))

                    if nuke_version >= 121 and SHUFFLE_TYPE:
                        shuffle = self.create_new_shuffle(layer, node)
                    else:
                        shuffle = self.create_old_shuffle(layer, node)

                    shuffle.autoplace()

                self.close()
            else:
                self._update_styles("regular")
        if event.key() == QtCore.Qt.Key_Control:
            self._update_styles("regular")

        self.shuffle_list = []

    def create_old_shuffle(self, target, node):
        shuffle = nuke.nodes.Shuffle(xpos=(node.xpos() + 100),
                                     ypos=(node.ypos() + 50),
                                     label='[value in]',
                                     inputs=[node],
                                     selected=True,
                                     out="rgba")
        shuffle["in"].setValue(self._channels[target.lower()])
        return shuffle

    def create_new_shuffle(self, target, node):
        """Lot of workaround needed to make sure proper channels are properly sorted and mapped.

        Args:
            target (str): Target channel to shuffle out.
            node (nuke.Node):  Node to shuffle channel out from.

        Returns:
            nuke.Node: New created Shuffle2 node.

        """
        shuffle = nuke.nodes.Shuffle2(xpos=(node.xpos() + 100),
                                      ypos=(node.ypos() + 50),
                                      label='[value in1]',
                                      inputs=[node],
                                      selected=True,
                                      in1=target,
                                      out1="rgba")

        if target == "alpha":
            channel_in = ['rgba.alpha' for _ in range(4)]
        else:
            channel_in = [layer for layer in node.channels() if layer.split(".")[0] == target]
            channel_in = self._sanity_channels(channel_in)

        channel_out = ('rgba.red', 'rgba.green', 'rgba.blue', 'rgba.alpha')
        in_2 = 0 if "depth.Z" in channel_in or "alpha" in channel_in else 1
        layer_in = (0, 0, 0, in_2)

        if "rgba.alpha" in channel_in:
            shuffle.knob("in2").setValue("rgba.alpha")

        mapping = (list((zip(layer_in, channel_in, channel_out))))
        print(mapping)
        shuffle.knob("mappings").setValue(mapping)
        return shuffle

    def _sanity_channels(self, layers):
        """For some reasons nuke node.channels() does not return consistent orders for r, g, b.

        Therefore ome re-ordering is necessary as well as connecting a single input to all 4 output layers.

        Args:
            layers (list): Layer names to re-order.

        """
        if len(layers) == 1 :
            layers = [layers[0] for _ in range(4)]
        elif len(layers) == 3:
            layers.append("rgba.alpha")
        d = {".red": 0, ".green": 1, ".blue": 2, ".alpha": 3}
        new_layer = [i for i in layers]
        for layer in new_layer:
            for k, v in d.items():
                if layer.endswith(k):
                    layers[v] = layer
        return layers

    def clicked(self):
        """Route click events based on key modifier."""
        modifiers = QtGuiWidgets.QApplication.keyboardModifiers()
        sender = self.sender()
        if modifiers == QtCore.Qt.ShiftModifier:
            channel = self.sender().text()
            if channel in self.shuffle_list:

                sender.setProperty("color", "regular")
                sender.setStyle(sender.style())
                self.shuffle_list.remove(channel)
            else:
                self.sender().setProperty("color", "purple_click")
                sender.setStyle(sender.style())
                self.shuffle_list.append(channel)

        elif modifiers == QtCore.Qt.ControlModifier:
            sender.setProperty("color", "blue_click")
            sender.setStyle(sender.style())
            node = self.active_viewer.input(nuke.activeViewer().activeInput())
            node.setSelected(True)
            grade = nuke.createNode("Grade")
            grade['channels'].setValue(self.sender().text())
            self.close()

        else:
            self.active_viewer['channels'].setValue(self.sender().text())
            self.close()

    def line_enter(self):
        """Change Viewer to completed text."""
        self.active_viewer['channels'].setValue(self._channels[self.input.text().lower()])
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
            nuke.message('No active viewer connected to node.')
    else:
        nuke.message('No viewer found in script.')
