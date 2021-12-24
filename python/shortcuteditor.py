from __future__ import division
from __future__ import print_function

import nuke
import os
try:
    # Prefer QtCore.Qt.py when available
    from Qt import QtCore, QtGui, QtWidgets, Qt
except ImportError:
    try:
        # PySide2 for default Nuke 11
        from PySide2 import QtCore, QtGui, QtWidgets
    except ImportError:
        # Or PySide for Nuke 10
        from PySide import QtCore, QtGui, QtGui as QtWidgets

__version__ = "1.2"


"""A shortcut-key editor for Nuke's menus

homepage: https://github.com/dbr/shortcuteditor-nuke
license: GPL v2

To use, in ~/.nuke/menu.py add this:

try:
    import shortcuteditor
    shortcuteditor.nuke_setup()
except Exception:
    import traceback
    traceback.print_exc()
"""


class KeySequenceWidget(QtWidgets.QWidget):
    """A widget to enter a keyboard shortcut.

    Loosely based on kkeysequencewidget.cpp from KDE :-)

    Modified from
    https://github.com/wbsoft/frescobaldi/blob/master/frescobaldi_app/widgets/keysequencewidget.py
    """

    keySequenceChanged = QtCore.Signal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.setLayout(layout)

        self.button = KeySequenceButton(self)
        self.clearButton = QtWidgets.QPushButton(self, iconSize=QtCore.QSize(16, 16))
        self.clearButton.setText("Clear")
        self.clearButton.setFixedWidth(50)

        layout.addWidget(self.button)
        layout.addWidget(self.clearButton)

        self.clearButton.clicked.connect(self.clear)

        self.button.setToolTip("Start recording a key sequence.")
        self.clearButton.setToolTip("Clear the key sequence.")

    def setShortcut(self, shortcut):
        """Sets the initial shortcut to display."""
        self.button.setKeySequence(shortcut)

    def shortcut(self):
        """Returns the currently set key sequence."""
        return self.button.keySequence()

    def clear(self):
        """Empties the displayed shortcut."""
        if self.button.isRecording():
            self.button.cancelRecording()
        if not self.button.keySequence().isEmpty():
            self.button.setKeySequence(QtGui.QKeySequence())
            self.keySequenceChanged.emit()

    def setModifierlessAllowed(self, allow):
        self.button._modifierlessAllowed = allow

    def isModifierlessAllowed(self):
        return self.button._modifierlessAllowed


class KeySequenceButton(QtWidgets.QPushButton):
    """
    Modified from
    https://github.com/wbsoft/frescobaldi/blob/master/frescobaldi_app/widgets/keysequencewidget.py
    """

    MAX_NUM_KEYSTROKES = 1

    def __init__(self, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        #self.setIcon(icons.get("configure"))
        self._modifierlessAllowed = True # True allows "b" as a shortcut, False requires shift/alt/ctrl/etc
        self._seq = QtGui.QKeySequence()
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._isrecording = False
        self.clicked.connect(self.startRecording)
        self._timer.timeout.connect(self.doneRecording)

    def setKeySequence(self, seq):
        self._seq = seq
        self.updateDisplay()

    def keySequence(self):
        if self._isrecording:
            self.doneRecording()
        return self._seq

    def updateDisplay(self):
        if self._isrecording:
            s = self._recseq.toString(QtGui.QKeySequence.NativeText).replace('&', '&&')
            if self._modifiers:
                if s: s += ","
                s += QtGui.QKeySequence(self._modifiers).toString(QtGui.QKeySequence.NativeText)
            elif self._recseq.isEmpty():
                s = "Input"
            s += " ..."
        else:
            s = self._seq.toString(QtGui.QKeySequence.NativeText).replace('&', '&&')
        self.setText(s)

    def isRecording(self):
        return self._isrecording

    def event(self, ev):
        if self._isrecording:
            # prevent Qt from special casing Tab and Backtab
            if ev.type() == QtCore.QEvent.KeyPress:
                self.keyPressEvent(ev)
                return True
        return QtWidgets.QPushButton.event(self, ev)

    def keyPressEvent(self, ev):
        if not self._isrecording:
            return QtWidgets.QPushButton.keyPressEvent(self, ev)
        if ev.isAutoRepeat():
            return
        #modifiers = int(ev.modifiers() & (QtCore.Qt.SHIFT | QtCore.Qt.CTRL | QtCore.Qt.ALT | QtCore.Qt.META))
        modifiers = ev.modifiers()

        ev.accept()

        key = ev.key()
        # check if key is a modifier or a character key without modifier (and if that is allowed)
        if (
            # don't append the key if the key is -1 (garbage) or a modifier ...
            key not in (-1, QtCore.Qt.Key_AltGr, QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control,
                            QtCore.Qt.Key_Alt, QtCore.Qt.Key_Meta, QtCore.Qt.Key_Menu)
            # or if this is the first key and without modifier and modifierless keys are not allowed
            and (self._modifierlessAllowed
                 or self._recseq.count() > 0
                 or modifiers & ~QtCore.Qt.SHIFT
                 or not ev.text()
                 or (modifiers & QtCore.Qt.SHIFT
                     and key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Space, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab,
                                 QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete, QtCore.Qt.Key_Escape)))):

            # change Shift+Backtab into Shift+Tab
            if key == QtCore.Qt.Key_Backtab and modifiers & QtCore.Qt.SHIFT:
                key = QtCore.Qt.Key_Tab | modifiers

            # remove the Shift modifier if it doen't make sense..
            elif (QtCore.Qt.Key_Exclam <= key <= QtCore.Qt.Key_At
                  # ... e.g ctrl+shift+! is impossible on, some,
                  # keyboards (because ! is shift+1)
                  or QtCore.Qt.Key_Z < key <= 0x0ff):
                key = key | (modifiers & ~int(QtCore.Qt.SHIFT))

            else:
                key = key | modifiers

            # append max number of keystrokes
            if self._recseq.count() < self.MAX_NUM_KEYSTROKES:
                l = list(self._recseq)
                l.append(key)
                self._recseq = QtGui.QKeySequence(*l)

        self._modifiers = modifiers
        self.controlTimer()
        self.updateDisplay()

    def keyReleaseEvent(self, ev):
        if not self._isrecording:
            return QtWidgets.QPushButton.keyReleaseEvent(self, ev)
        modifiers = int(ev.modifiers() & (QtCore.Qt.SHIFT | QtCore.Qt.CTRL | QtCore.Qt.ALT | QtCore.Qt.META))
        ev.accept()

        self._modifiers = modifiers
        self.controlTimer()
        self.updateDisplay()

    def hideEvent(self, ev):
        if self._isrecording:
            self.cancelRecording()
        QtWidgets.QPushButton.hideEvent(self, ev)

    def controlTimer(self):
        if self._modifiers or self._recseq.isEmpty():
            self._timer.stop()
        else:
            self._timer.start(600)

    def startRecording(self):
        #self.setFocus(True) # because of QTBUG 17810
        self.setDown(True)
        self.setStyleSheet("text-align: left;")
        self._isrecording = True
        self._recseq = QtGui.QKeySequence()
        self._modifiers = int(QtWidgets.QApplication.keyboardModifiers() & (QtCore.Qt.SHIFT | QtCore.Qt.CTRL | QtCore.Qt.ALT | QtCore.Qt.META))
        self.grabKeyboard()
        self.updateDisplay()

    def doneRecording(self):
        self._seq = self._recseq
        self.cancelRecording()
        self.clearFocus()
        self.parentWidget().keySequenceChanged.emit()

    def cancelRecording(self):
        if not self._isrecording:
            return
        self.setDown(False)
        self.setStyleSheet("")
        self._isrecording = False
        self.releaseKeyboard()
        self.updateDisplay()





def _find_menu_items(menu, _path = None, _top_menu_name = None):
    """Extracts items from a given Nuke menu

    Returns a list of strings, with the path to each item

    Ignores divider lines and hidden items (ones like "@;&CopyBranch" for shift+k)

    >>> found = _find_menu_items(nuke.menu("Nodes"))
    >>> found.sort()
    >>> found[:5]
    ['3D/Axis', '3D/Camera', '3D/CameraTracker', '3D/DepthGenerator', '3D/Geometry/Card']
    """

    if _top_menu_name is None:
        _top_menu_name = menu.name()

    found = []

    mi = list(menu.items())
    for i in mi:
        if isinstance(i, nuke.Menu):
            # Sub-menu, recurse
            mname = i.name().replace("&", "")
            subpath = "/".join(x for x in (_path, mname) if x is not None)
            sub_found = _find_menu_items(menu = i, _path = subpath, _top_menu_name = _top_menu_name)
            found.extend(sub_found)
        elif isinstance(i, nuke.MenuItem):
            if i.name() == "":
                # Skip dividers
                continue
            if i.name().startswith("@;"):
                # Skip hidden items
                continue

            subpath = "/".join(x for x in (_path, i.name()) if x is not None)
            found.append({'menuobj': i, 'menupath': subpath, 'top_menu_name': _top_menu_name})

    return found


def _widget_with_label(towrap, text):
    """Wraps the given widget in a layout, with a label to the left
    """
    w = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    label = QtWidgets.QLabel(text)
    label.setAlignment(QtCore.Qt.AlignRight)
    layout.addWidget(label)
    layout.addWidget(towrap)
    w.setLayout(layout)
    return w


def _load_yaml(path):
    def _load_internal():
        import json
        if not os.path.isfile(path):
            # print "Settings file %r does not exist" % (path)
            return
        f = open(path)
        overrides = json.load(f)
        f.close()
        return overrides

    # Catch any errors, print traceback and continue
    try:
        return _load_internal()
    except Exception:
        print("Error loading %r" % path)
        import traceback
        traceback.print_exc()

        return None


def _save_yaml(obj, path):
    def _save_internal():
        import json
        ndir = os.path.dirname(path)
        if not os.path.isdir(ndir):
            try:
                os.makedirs(ndir)
            except OSError as e:
                if e.errno != 17: # errno 17 is "already exists"
                    raise

        f = open(path, "w")
        # TODO: Limit number of saved items to some sane number
        json.dump(obj, fp = f, sort_keys=True, indent=1, separators=(',', ': '))
        f.write("\n")
        f.close()

    # Catch any errors, print traceback and continue
    try:
        _save_internal()
    except Exception:
        print("Error saving node weights")
        import traceback
        traceback.print_exc()


def _restore_overrides(overrides):
    for item, key in list(overrides.items()):
        menu_name, _, path = item.partition("/")
        m = nuke.menu(menu_name)
        item = m.findItem(path)
        if item is None:
            nuke.warning("WARNING: %r (menu: %r) does not exist?" % (path, menu_name))
        else:
            #print "Restoring shortcut %r for %r (menu: %r)" % (key, path, menu_name)
            item.setShortcut(key)


def _overrides_as_code(overrides):
    menus = {}
    for item, key in list(overrides.items()):
        menu_name, _, path = item.partition("/")

        menus.setdefault(menu_name, []).append((path, key))


    lines = []
    lines.append("def apply_key_overrides():")
    lines.append("    overrides = {")
    for menu, all_path_key in list(menus.items()):
        lines.append("        'Nuke': [")
        for path, key in all_path_key:
            lines.append("            (%r, %r)," % (path, key))
        lines.append("        ],")
        lines.append("    }")
        lines.append("    for menu_name, overrides in overrides:")
        lines.append("        m = nuke.menu(menu_name)")
        lines.append("        for path, key in overrides:")
        lines.append("            item = m.findItem(path)")
        lines.append("            if item is None:")
        lines.append("                print 'WARNING: %r (menu: %r) does not exist, cannot restore key %r' % (path, menu, key)")
        lines.append("            else:")
        lines.append("                item.setShortcut(key)")
        return "\n".join(lines)


    lines.append("apply_key_overrides()")
    return "\n".join(lines)


class Overrides(object):
    def __init__(self):
        self.settings_path = os.path.expanduser("~/.nuke/shortcuteditor_settings.json")

    def save(self):
        settings = {
            'overrides': self.overrides,
            'version': 1,
            }
        _save_yaml(obj=settings, path=self.settings_path)

    def clear(self):
        self.overrides = {}
        self.save()

    def restore(self):
        """Load the settings from disc, and update Nuke
        """
        settings = _load_yaml(path=self.settings_path)

        # Default
        self.overrides = {}

        if settings is None:
            return

        elif int(settings['version']) == 1:
            self.overrides = settings['overrides']
            _restore_overrides(self.overrides)

        else:
            nuke.warning("Wrong version of shortcut, nothing loaded (version was %s expected 1), path was %r" % (
                    int(settings['version']),
                    self.settings_path))
            return



class ShortcutEditorWidget(QtWidgets.QDialog):
    closed = QtCore.Signal()

    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        # Load settings from disc, and into Nuke
        self.settings = Overrides()
        self.settings.restore()

        # Window setup
        self.setWindowTitle("Shortcut editor")
        self.setMinimumSize(600, 500)

        # Internal things
        self._search_timer = None
        self._cache_items = None

        # Stack widgets atop each other
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Search group
        search_group = QtWidgets.QGroupBox("Filtering")
        search_layout = QtWidgets.QHBoxLayout()
        search_group.setLayout(search_layout)

        layout.addWidget(search_group)

        # By-key filter bar
        key_filter = KeySequenceWidget()
        key_filter.keySequenceChanged.connect(self.populate)
        self.key_filter = key_filter


        search_layout.addWidget(_widget_with_label(key_filter, "Search by key"))

        # text filter bar
        search_input = QtWidgets.QLineEdit()
        search_input.textChanged.connect(self.search)
        self.search_input = search_input
        search_layout.addWidget(
            _widget_with_label(search_input, "Search by text"))

        # Main table
        table = QtWidgets.QTableWidget()
        table.setColumnCount(2)

        table.setColumnWidth(0, 150)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)

        self.table = table
        layout.addWidget(table)

        # Buttons at bottom
        button_reset = QtWidgets.QPushButton("Reset...")
        button_reset.clicked.connect(self.reset)
        layout.addWidget(button_reset)
        self.button_reset = button_reset


        button_close = QtWidgets.QPushButton("Close")
        button_close.clicked.connect(self.close)
        layout.addWidget(button_close)
        self.button_close = button_close

        # Go
        self.populate()

    def search(self):
        """Handles changes to search box

        Gives a slight delay between filtering the list, so quickly
        typing doesn't update once for every letter
        """
        if self._search_timer is not None:
            # Timer already set, reset
            self._search_timer.stop()
            self._search_timer.start(200)
        else:
            self._search_timer = QtCore.QTimer()
            self._search_timer.setSingleShot(True)
            self._search_timer.timeout.connect(self.populate)
            self._search_timer.start(200) # 200ms timeout

    def list_menu(self):
        """Gets the list-of-dicts containing all menu items

        Caches for speed of filtering
        """
        if self._cache_items is not None:
            return self._cache_items
        else:
            items = []
            for menu in ("Nodes", "Nuke", "Viewer", "Node Graph"):
                items.extend(_find_menu_items(nuke.menu(menu)))
            self._cache_items = items
            return items

    def populate(self):
        # Get menu items
        menu_items = self.list_menu()

        # ..and filter them, first by the input text
        search = self.search_input.text()
        menu_items = [x for x in menu_items
                      if search.lower() in x['menupath'].lower().replace("&", "")]

        # ..and also filter by the shortcut, if one is specified
        if self.key_filter.shortcut().toString() != "":
            menu_items = [x for x in menu_items
                          if x['menuobj'].shortcut() == self.key_filter.shortcut()]

        # Setup table
        self.table.clear()
        self.table.setRowCount(len(menu_items))
        self.table.setHorizontalHeaderLabels(['Shortcut', 'Menu location'])

        # Add items
        for rownum, menuitem in enumerate(menu_items):
            shortcut = QtGui.QKeySequence(menuitem['menuobj'].shortcut())

            w = KeySequenceWidget()
            w.setShortcut(shortcut)

            self.table.setCellWidget(rownum, 0, w)
            self.table.setCellWidget(rownum, 1, QtWidgets.QLabel("%s (menu: %s)" % (menuitem['menupath'], menuitem['top_menu_name'])))

            w.keySequenceChanged.connect(lambda menuitem=menuitem, w=w: self.setkey(menuitem = menuitem, shortcut_widget=w))

    def setkey(self, menuitem, shortcut_widget):
        """Called when shortcut is edited

        Updates the Nuke menu, and puts the key in the Overrides setting-thing
        """
        menuitem['menuobj'].setShortcut(shortcut_widget.shortcut().toString())
        self.settings.overrides["%s/%s" % (menuitem['top_menu_name'], menuitem['menupath'])] = shortcut_widget.shortcut().toString()

    def reset(self):
        """Reset some or all of the key overrides
        """

        mb = QtWidgets.QMessageBox(
            self,
            )

        mb.setText("Clear all key overrides?")
        mb.setInformativeText("Really remove all %s key overrides?" % len(self.settings.overrides))
        mb.setDetailedText(
            "Will reset the following to defaults:\n\n"
            + "\n".join("%s (key: %s)" % (p, k or "(blank)") for (p, k) in list(self.settings.overrides.items())))

        mb.setIcon(QtWidgets.QMessageBox.Warning)

        mb.setStandardButtons(QtWidgets.QMessageBox.Reset | QtWidgets.QMessageBox.Cancel)
        mb.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        ret = mb.exec_()

        if ret == QtWidgets.QMessageBox.Reset:
            self.settings.clear()
            self.close()
            QtWidgets.QMessageBox.information(None, "Reset complete", "You must restart Nuke for this to take effect")
        elif ret == QtWidgets.QMessageBox.Cancel:
            pass
        else:
            raise RuntimeError("Unhandled button")

    def closeEvent(self, evt):
        """Save when closing the UI
        """

        self.settings.save()
        self.closed.emit()
        QtWidgets.QWidget.closeEvent(self, evt)

    def undercursor(self):
        def clamp(val, mi, ma):
            return max(min(val, ma), mi)

        # Get cursor position, and screen dimensions on active screen
        cursor = QtWidgets.QCursor().pos()
        screen = QtWidgets.QDesktopWidget().screenGeometry(cursor)

        # Get window position so cursor is just over text input
        xpos = cursor.x() - (self.width()/2)
        ypos = cursor.y() - 13

        # Clamp window location to prevent it going offscreen
        xpos = clamp(xpos, screen.left(), screen.right() - self.width())
        ypos = clamp(ypos, screen.top(), screen.bottom() - (self.height()-13))

        # Move window
        self.move(xpos, ypos)


def load_shortcuts():
    """Load the settings from disc

    Could be called from menu.py (see module docstring at start of
    file for an example)
    """
    s = Overrides()
    s.restore()


_sew_instance = None
def gui():
    """Launch the key-override editor GUI

    Could be called from menu.py (see module docstring at start of
    file for an example)
    """
    global _sew_instance

    if _sew_instance is not None:
        # Already an instance (make it really obvious - focused, in
        # front and under cursor, like other Nuke GUI windows)
        _sew_instance.show()
        _sew_instance.undercursor()
        _sew_instance.setFocus()
        _sew_instance.activateWindow()
        _sew_instance.raise_()
        return

    # Make a new instance, keeping it in a global variable to avoid
    # multiple instances being opened
    _sew_instance = ShortcutEditorWidget()

    def when_closed():
        global _sew_instance
        _sew_instance = None
    _sew_instance.closed.connect(when_closed)

    modal=False
    if modal:
        _sew_instance.exec_()
    else:
        _sew_instance.show()



def nuke_setup():
    """Call this from menu.py to setup stuff
    """

    # Load saved shortcuts once Nuke has started up (i.e when it has
    # created the Root node - otherwise some menu items might be
    # created after this function runs)
    nuke.addOnCreate(lambda: load_shortcuts(), nodeClass="Root")

    # Menu item to open shortcut editor
    nuke.menu("Nuke").addCommand("Edit/Edit keyboard shortcuts", gui)


nuke_setup()
