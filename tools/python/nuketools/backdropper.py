
import nuke
import colorsys

if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
else:
    from PySide2 import QtWidgets, QtGui, QtCore

from QtUtils import CodeTextEdit


nuke.menu('Nuke').addCommand('Edit/Node/Backdropper', 'backdropper.invoke()', 'shift+b')



# Color conversion utility functions
def dec2rgb(dec, fp=True):
    # Convert nuke style hexadecimal to 8 bit integer rgb tuple
    # if fp: return 0-1 float instead of 0-255 int
    hexcol = '%08x' % dec
    rgb = (int(hexcol[0:2], 16), int(hexcol[2:4], 16), int(hexcol[4:6], 16))
    if fp:
        rgb = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    return rgb

def rgb2hex(rgb, fp=True):
    # Convert 8 bit integer rgb tuple to hexadecimal rgb value
    if fp:
        rgb = (rgb[0]*255, rgb[1]*255, rgb[2]*255)
    return '%02x%02x%02x' % rgb

def hex2rgb(hexcol, fp=True):
    # Convert hex color to rgb 0-1 float
    hexcol = hexcol.lstrip('#')
    ln = len(hexcol)
    rgb = tuple(int(hexcol[i:i + ln // 3], 16) for i in range(0, ln, ln // 3))
    if fp:
        rgb = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    return rgb

def rgb2dec(rgb, fp=True):
    # Convert rgb 0-1 float tuple to nuke style integer hexadecimal 
    if fp:
        rgb = (rgb[0]*255, rgb[1]*255, rgb[2]*255)
    return int('%02x%02x%02x%02x' % (rgb[0], rgb[1], rgb[2], 1), 16)

def rgb2hsv(rgb, fp=True):
    if not fp:
        rgb = (rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    return colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])

def hsv2rgb(hsv, fp=True):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    if not fp:
        rgb = (rgb[0]*255, rgb[1]*255, rgb[2]*255)
    return rgb

def dec2hex(dec):
    rgb = dec2rgb(dec)
    return rgb2hex(rgb)

def hex2dec(hexcol):
    rgb = hex2rgb(hexcol)
    return rgb2dec(rgb)




class ColorPatch(QtWidgets.QPushButton):
    ''' Square color patch for setting colors 
    '''
    def __init__(self, rgb):
        super(ColorPatch, self).__init__()
        self.setText('')
        
        # Make square
        self.setMaximumWidth(self.sizeHint().height())
        hexcol = rgb2hex(rgb)
        self.setStyleSheet('border-size: 0px; background-color: #{0}'.format(hexcol))
        # self.btn_col_bg.setFlat(True)


class ColorPatchBox(QtWidgets.QHBoxLayout):
    ''' Container for colorpatches
    '''
    def __init__(self):
        super(ColorPatchBox, self).__init__()
        self.addStretch(0)
        self.setContentsMargins(0,0,0,0)
        self.setSpacing(0)



class BackdropPanel(QtWidgets.QDialog):
    ''' Show an interface to create or modify a BackdropNode
    '''
    def __init__(self, parent):
        super(BackdropPanel, self).__init__(parent)
        self.setup_ui()
        self.setup_nodes()

    def setup_ui(self):
        # Set up the user interface
        self.layout = QtWidgets.QVBoxLayout()

        # self.text = QtWidgets.QPlainTextEdit()
        self.text = CodeTextEdit() # Use our souped-up code editor widget from Knob Scripter
        self.text.textChanged.connect(self.save) 
        self.layout.addWidget(self.text)

        self.bx_color_presets = ColorPatchBox()


        preset_colors = [
            (0.00, 0.00, 0.12),
            (0.00, 0.00, 0.16),
            (0.00, 0.00, 0.24),
            (0.00, 0.00, 0.33),
            (0.00, 0.00, 0.50),
            (0.00, 0.00, 0.70),
            (0.11, 0.22, 0.24),
            (0.33, 0.22, 0.24),
            (0.50, 0.22, 0.24),
            (0.58, 0.22, 0.24),
            (0.62, 0.22, 0.24),
            (0.72, 0.22, 0.24),
            (0.11, 0.22, 0.33),
            (0.33, 0.22, 0.33),
            (0.50, 0.22, 0.33),
            (0.58, 0.22, 0.33),
            (0.62, 0.22, 0.33),
            (0.72, 0.22, 0.33),
            (0.94, 0.22, 0.33),
            (0.11, 0.33, 0.33),
            (0.33, 0.33, 0.33),
            (0.62, 0.33, 0.33),
            (0.94, 0.33, 0.33),
        ]


        for color in preset_colors:
            rgb = hsv2rgb(color)
            btn = ColorPatch(rgb)
            btn.clicked.connect(self.set_tile_color_from_patch)
            self.bx_color_presets.addWidget(btn)
        self.layout.addLayout(self.bx_color_presets)


        for label in ['Hue', 'Sat', 'Val']:
            self.add_slider_box(label)

        # Create other config options
        # Font size slider
        hbox_note_font_size = QtWidgets.QHBoxLayout()
        note_font_size_label = QtWidgets.QLabel('Font Size')
        hbox_note_font_size.addWidget(note_font_size_label)
        self.note_font_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.note_font_size_slider.setMinimum(10)
        self.note_font_size_slider.setMaximum(200)
        self.note_font_size_slider.valueChanged.connect(self.set_note_font_size)
        hbox_note_font_size.addWidget(self.note_font_size_slider)
        self.layout.addLayout(hbox_note_font_size)

        # Font color slider
        hbox_note_font_color = QtWidgets.QHBoxLayout()
        note_font_color_label = QtWidgets.QLabel('Font Color')
        hbox_note_font_color.addWidget(note_font_color_label)
        self.note_font_color_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.note_font_color_slider.valueChanged.connect(self.set_note_font_color)
        hbox_note_font_color.addWidget(self.note_font_color_slider)
        self.layout.addLayout(hbox_note_font_color)

        # Appearance switcher
        hbox_style = QtWidgets.QHBoxLayout()
        self.appearance_checkbox = QtWidgets.QCheckBox('Appearance: Border')
        self.appearance_checkbox.stateChanged.connect(self.set_appearance)
        hbox_style.addWidget(self.appearance_checkbox)

        # Border width slider
        border_width_slider_label = QtWidgets.QLabel('Border Width')
        hbox_style.addWidget(border_width_slider_label)
        self.border_width_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.border_width_slider.setMaximum(14)
        self.border_width_slider.valueChanged.connect(self.set_border_width)
        hbox_style.addWidget(self.border_width_slider)
        
        self.layout.addLayout(hbox_style)


        # Create Ok / Cancel buttons
        btn_ok = QtWidgets.QPushButton('Ok')
        btn_ok.clicked.connect(self.save_and_quit)
        btn_exit = QtWidgets.QPushButton('Cancel')
        btn_exit.clicked.connect(self.quit)
        
        # Create hbox widget for buttons
        btnbox_bottom = QtWidgets.QHBoxLayout()
        btnbox_bottom.addWidget(btn_ok)
        btnbox_bottom.addWidget(btn_exit)
        
        # Add button box to self.layout
        self.layout.addLayout(btnbox_bottom)
        
        self.setLayout(self.layout)
        self.setWindowTitle('Backdrop')
        self.resize(500, 500)
        self.setMinimumSize(self.sizeHint().width(), self.sizeHint().height())
        self.move(QtGui.QCursor().pos() - QtCore.QPoint(32,74))
        # self.show()


    def add_slider_box(self, label):
        # Add QSlider with label, assign sliders to vars
        hbox = QtWidgets.QHBoxLayout()
        lab = QtWidgets.QLabel(label)
        hbox.addWidget(lab)
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.valueChanged.connect(self.set_tile_color_from_sliders)
        hbox.addWidget(slider)
        self.layout.addLayout(hbox)
        if label == 'Hue':
            self.slider_hue = slider
        elif label == 'Sat':
            self.slider_sat = slider
        elif label == 'Val':
            self.slider_val = slider


    def setup_nodes(self):
        nodes = nuke.selectedNodes()

        self.bd = None

        self.bd_defaults = {
            'note_font_size': 24,
            'note_font': 'Helvetica',
            'note_font_color': 4294967295,
            'text_color': '000000',
            'tile_color': 1145324799,
            'appearance': 'Fill',
            'z_order': -10,
            'bdwidth': 300,
            'bdheight': 300,
        }

        if nodes:
            # If last selected node is a BackdropNode, we edit it.
            # Otherwise, we create a new one based on the selection.
            if nodes[-1].Class() == 'BackdropNode':
                self.bd = nodes[-1]
                self.get_text()
            # Get min existing z_order, put this backdrop behind all existing ones.
            z_orders = [n['z_order'].getValue() for n in nodes if n.Class() == 'BackdropNode']
            if z_orders:
                z_orders.sort()
                self.bd_defaults['z_order'] = z_orders[0] - 10

        # If no backdrop, create one
        if not self.bd:
            self.create_bd(nodes)

        self.appearance_exists = 'appearance' in self.bd.knobs()
        self.border_width_exists = 'border_width' in self.bd.knobs()

        # Set sliders from Backdrop
        self.set_sliders()


    def set_appearance(self):
        sender = self.sender()
        state = sender.isChecked()
        if self.appearance_exists:
            if state:
                self.bd['appearance'].setValue(1)
            else:
                self.bd['appearance'].setValue(0)


    def set_note_font_size(self):
        sender = self.sender()
        self.bd['note_font_size'].setValue(sender.value())


    def set_note_font_color(self):
        sender = self.sender()
        # self.bd['note_font_color'].setValue(sender.value())
        value = sender.value() / 100.0
        hexcol = rgb2hex(hsv2rgb((0, 0, value)))
        self.bd_defaults['text_color'] = hexcol
        self.save()

    def set_border_width(self):
        if self.border_width_exists:
            self.bd['border_width'].setValue(self.sender().value())


    def set_tile_color_from_sliders(self):
        hsv = (self.slider_hue.value()/100.0, self.slider_sat.value()/100.0, self.slider_val.value()/100.0)
        rgb = hsv2rgb(hsv)
        dec = rgb2dec(rgb)
        self.bd['tile_color'].setValue(dec)


    def set_tile_color_from_patch(self):
        sender = self.sender()
        style = sender.styleSheet()
        pattern = 'background-color: #'
        if pattern in style:
            sender_hex = style.split(pattern)[-1]
        else:
            return
        rgb = hex2rgb(sender_hex)
        dec = rgb2dec(rgb)
        self.bd['tile_color'].setValue(dec)
        self.set_sliders()


    def set_sliders(self):
        # Get tile color from Backdrop and set hsv sliders
        curhsv = rgb2hsv(dec2rgb(self.bd['tile_color'].value()))
        self.slider_hue.setValue(curhsv[0]*100)
        self.slider_sat.setValue(curhsv[1]*100)
        self.slider_val.setValue(curhsv[2]*100)
        self.note_font_size_slider.setValue(self.bd['note_font_size'].getValue())
        if self.appearance_exists:
            self.appearance_checkbox.setChecked(self.bd['appearance'].getValue())
        # set text color
        rgb = hex2rgb(self.bd_defaults['text_color'])
        hsv = rgb2hsv(rgb)
        self.note_font_color_slider.setValue(hsv[2]*100)
        if self.border_width_exists:
            self.border_width_slider.setValue(self.bd['border_width'].getValue())


    def set_color(self):
        ''' Prompt user for a color, and set the bg color of the sender to that color
            # http://zetcode.com/gui/pyqt5/eventssignals/
        '''
        sender = self.sender()
        color = nuke.getColor()
        color_hex = nkhex2hex(color)

        # Set button bg color to user color
        # sender.setStyleSheet('background-color: #{0}'.format(color_hex))

        if sender.text() == 'BG':
            self.bd['tile_color'].setValue(color)
        elif sender.text() == 'Text':
            self.bd['note_font_color'].setValue(color)


    def create_bd(self, nodes):
        ''' Create backdrop node. If nodes are selected, set size and font size
        '''
        _ = [n.setSelected(False) for n in nuke.allNodes(recurseGroups=True)]

        # Create backdrop and set default knob values
        self.bd = nuke.createNode('BackdropNode')
        for knob, value in self.bd_defaults.iteritems():
            if knob in self.bd.knobs():
                self.bd[knob].setValue(value)

        if nodes:
            # Find dimensions of selected nodes
            positions = [[n.xpos() + n.screenWidth()/2, n.ypos() + n.screenHeight()/2] 
                for n in nodes]
            sorted_x = sorted(positions, key=lambda v: v[0])
            sorted_y = sorted(positions, key=lambda v: v[1])
            screen_size = (nodes[0].screenWidth()/2, nodes[0].screenHeight()/2)
            minpos = (sorted_x[0][0], sorted_y[0][1])
            maxpos = (sorted_x[-1][0], sorted_y[-1][1])
            margin = (50, 60, 50) # sides, top, bottom

            # Set Backdrop size - XYpos is top left corner, +x is right, +y is down, bdwidth * bdheight = size
            self.bd.setXYpos(
                minpos[0] - screen_size[0] - margin[0],
                minpos[1] - screen_size[1] - margin[1]
                )
            self.bd['bdwidth'].setValue(maxpos[0]-minpos[0] + screen_size[0]*2 + margin[0]*2)
            self.bd['bdheight'].setValue(maxpos[1]-minpos[1] + screen_size[1]*2 + margin[2]+margin[1])
        
        # Init font size from bdwidth
        bd_width = self.bd['bdwidth'].getValue()
        # Font size is hard-coded ratio
        font_size = round(bd_width / 34.0)
        # Clamp to sensible range
        font_size = max(10, min(font_size, 200))
        self.bd['note_font_size'].setValue(font_size)

        # Restore selection
        _ = [n.setSelected(True) for n in nodes]


    def save(self):
        ''' Save current edits to the backdrop node
            # Line 1 is our header
            # Line 2 is our subheader
            # Line 3:-1 is the text body
        '''
        label = self.text.document().toPlainText()
        if not label:
            return
        lines = label.split('\n')
        if not lines:
            return
        
        lines[0] = '<font color=#{0}><font size=7><b>{1}</b></font>'.format(
            self.bd_defaults.get('text_color'),
            lines[0])
        if len(lines) > 1:
            lines[1] = '<font size=4><b>{0}</b></font><font size=2>'.format(lines[1])
            lines.append('\n</font>')
        self.bd['label'].setValue('\n'.join(lines))


    def get_text(self):
        ''' Read text from Backdrop's label and set text, removing formatting
        '''
        label = self.bd['label'].getValue()
        if not label:
            return
        lines = label.split('\n')
        if not lines:
            return
        label = list()
        if '<b>' in lines[0] and '</b>' in lines[0]:
            label.append(lines[0].split('<b>')[-1].split('</b>')[0])
        else:
            label.append(lines[0])
        if len(lines) > 1:
            if '<b>' in lines[1] and '</b>' in lines[1]:
                label.append(lines[1].split('<b>')[-1].split('</b>')[0])
            else:
                label.append(lines[1])
        if len(lines) > 2:
            if '<font size=2>' in lines[2]:
                label.append(lines[2].split('<font size=2>')[-1])
            else:
                label.append(lines[2])
        label += lines[3:]
        if label[-1].endswith('</font>'):
            label[-1] = label[-1].split('</font>')[0]
        self.text.appendPlainText('\n'.join(label))

        # Set self.bd_defaults['text_color'] from first line
        if '<font color=#' in lines[0] and '><font size=' in lines[0]:
            hex_col = lines[0].split('<font color=#')[-1].split('><font size=')[0]
            self.bd_defaults['text_color'] = hex_col


    def keyPressEvent(self, event):
        '''Handle keyboard events.'''
        key = event.key()
        ctrl = bool(event.modifiers() & QtCore.Qt.ControlModifier)
        alt = bool(event.modifiers() & QtCore.Qt.AltModifier)
        shift = bool(event.modifiers() & QtCore.Qt.ShiftModifier)
        if key == QtCore.Qt.Key_Escape:
            self.quit()
        if (key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter) and ctrl:
            self.save_and_quit()
        if ctrl and key == QtCore.Qt.Key_S:
            self.save()
            self.close()
        if alt and key == QtCore.Qt.Key_A:
            self.save()
            self.close()


    def quit(self):
        self.close()


    def save_and_quit(self):
        self.save()
        self.close()



def invoke():
    panel = BackdropPanel(QtWidgets.QApplication.activeWindow())
    panel.show()