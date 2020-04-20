import nuke
import colorsys

if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
    from PySide.QtCore import Qt
else:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Qt


from QtUtils import CodeTextEdit

nuke.menu('Nuke').addCommand('Edit/Node/Backdropper', 'reload(backdropper);backdropper.invoke()', 'shift+b')

'''
# Create and edit backdrop nodes
    Create a new backdrop node given a node selection, or create one of a default size
    Create panel shows:
        - Header 
        - Sub-Header
        - Text mutliline input field
        - option for preformatted text
        - color (colorchip)
        - presets dropdown (light / dark pastels?)
    Edit existing backdrop node
        (nuke.selectedNodes()[-1] = selected backdrop)
        - populate fields with contents
'''

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




class BackdropPanel(QtWidgets.QWidget):
    ''' Show an interface to create or modify a BackdropNode
    '''
    def __init__(self):
        super(BackdropPanel, self).__init__()

        self.setup_ui()
        self.setup_nodes()

        # Invoke window

        # self.show()


    def setup_ui(self):
        # Set up the user interface
        self.layout = QtWidgets.QVBoxLayout()

        # self.text = QtWidgets.QPlainTextEdit()
        self.text = CodeTextEdit() # Use our souped-up code editor widget from Knob Scripter
        self.layout.addWidget(self.text)

        # Value Buttons
        self.bx_color_values = ColorPatchBox()
        # color_label = QtWidgets.QLabel('Color')
        ln = 14
        for i in range(ln):
            print i
            hsv = (0.0, 0.0, 0.0+1.0/ln*i)
            print hsv
            rgb = hsv2rgb(hsv)
            btn = ColorPatch(rgb)
            btn.clicked.connect(self.set_tile_color)
            self.bx_color_values.addWidget(btn)
        self.layout.addLayout(self.bx_color_values)

        # Hue Buttons
        self.bx_color_hues = ColorPatchBox()
        # color_label = QtWidgets.QLabel('Color')
        ln = 14
        for i in range(ln):
            print i
            hsv = (0.0+1.0/ln*(i), 0.2, 0.5)
            print hsv
            rgb = hsv2rgb(hsv)
            btn = ColorPatch(rgb)
            btn.clicked.connect(self.set_tile_color)
            self.bx_color_hues.addWidget(btn)
        self.layout.addLayout(self.bx_color_hues)
        
        
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
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Set Backdrop')
        self.resize(500, 500)
        self.setMinimumSize(self.sizeHint().width(), self.sizeHint().height())
        # self.under_cursor()
        self.move(QtGui.QCursor().pos() - QtCore.QPoint(32,74))



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
            if nodes[0].Class() == 'BackdropNode':
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


    def set_tile_color(self):
        sender = self.sender()
        
        adjust_hue = False
        adjust_val = False
        # Check if button is  in color hues or color values.
        val_idx = self.bx_color_values.indexOf(sender)
        hue_idx = self.bx_color_hues.indexOf(sender)
        if val_idx != -1:
            print 'BTN in VAL!'
            adjust_val = True
        if hue_idx != -1:
            print 'BTN in HUE!'
            adjust_hue = True


        style = sender.styleSheet()
        pattern = 'background-color: #'
        if pattern in style:
            sender_hex = style.split(pattern)[-1]
        else:
            return

        print 'BTN color HEX', sender_hex

        sender_rgb = hex2rgb(sender_hex)
        sender_hsv = rgb2hsv(sender_rgb)

        currgb = dec2rgb(self.bd['tile_color'].value())
        print 'Current RGB', currgb

        curhsv = rgb2hsv(currgb)
        print 'Current HSV', curhsv

        if adjust_hue:
            # Adjust hue without changing value
            newhsv = (sender_hsv[0], sender_hsv[1], curhsv[2])
        if adjust_val:
            # Adjust value without changing hue
            newhsv = (curhsv[0], curhsv[1], sender_hsv[2])
        print 'New HSV:', newhsv
        new_rgb = hsv2rgb(newhsv)
        print 'NEW RGB:', new_rgb
        dec = rgb2dec(new_rgb)
        self.bd['tile_color'].setValue(dec)




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

        '''
            I'm thinking maybe a row of color patches at the bottom to 
            set the tile_color
            and maybe the font color is another row
            maybe a button to select a color that sets it to a custom color
            int knobs for z_order and font size? Presets for font scale?

        '''


    
    def create_bd(self, nodes):
        ''' Create backdrop node. If nodes are selected, set size.
        '''
        _ = [n.setSelected(False) for n in nuke.allNodes(recurseGroups=True)]

        # Create backdrop and set default knob values
        self.bd = nuke.createNode('BackdropNode')
        for knob, value in self.bd_defaults.iteritems():
            if knob in self.bd.knobs():
                self.bd[knob].setValue(value)

        if nodes:
            positions = [[n.xpos() + n.screenWidth()/2, n.ypos() + n.screenHeight()/2] 
                for n in nodes]
            sorted_x = sorted(positions, key=lambda v: v[0])
            sorted_y = sorted(positions, key=lambda v: v[1])
            screen_size = (nodes[0].screenWidth()/2, nodes[0].screenHeight()/2)
            minpos = (sorted_x[0][0], sorted_y[0][1])
            maxpos = (sorted_x[-1][0], sorted_y[-1][1])
            margin = (50, 60, 50) # sides, top, bottom

            # Set Backdrop size - XYpos is top left corner +x is right, +y is down
            self.bd.setXYpos(
                minpos[0] - screen_size[0] - margin[0],
                minpos[1] - screen_size[1] - margin[1]
                )
            self.bd['bdwidth'].setValue(maxpos[0]-minpos[0] + screen_size[0]*2 + margin[0]*2)
            self.bd['bdheight'].setValue(maxpos[1]-minpos[1] + screen_size[1]*2 + margin[2]+margin[1])
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
            lines[1] = '<font size=4><b>{0}</b></font>'.format(lines[1])
            lines.append('\n</font>')
        if len(lines) > 2:
            lines[2] = '<font size=2>{0}'.format(lines[2])
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


    def keyPressEvent(self, event):
        '''Handle keyboard events.'''
        key = event.key()
        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        alt = bool(event.modifiers() & Qt.AltModifier)
        shift = bool(event.modifiers() & Qt.ShiftModifier)
        if key == QtCore.Qt.Key_Escape:
            self.quit()
        if (key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter) and ctrl:
            self.save_and_quit()
        if ctrl and key == QtCore.Qt.Key_S:
            self.save()

    def quit(self):
        self.close()

    def save_and_quit(self):
        self.save()
        self.close()



def invoke():
    global panel
    panel = BackdropPanel()
    # panel.setWindowFlags(QtCore.Qt.Tool)
    panel.show()  # Show the UI




# # Get the grid size from the preferences. Used as the default unit of movement.
# grid = (int(nuke.toNode('preferences').knob('GridWidth').value()), int(nuke.toNode('preferences').knob('GridHeight').value()))


# MARGIN = [grid[0]*1, grid[1]*4]


# def create_backdrop(settings):
#     # Create a backdrop node with given settings
#     # param: dict: settings - 
#     pass



# def show_panel(node=None):
#     # Show a backdrop panel and return the settings
#     # param: node object - optional backdrop node to populate settings from

#     # dict for mapping font sizes
#     font_sizes = {
#         'small': 14,
#         'medium': 24,
#         'large': 48,
#         'huge': 96,
#     }

#     # Get existing values if any
#     # if not node:
#     settings = {
#         'tile_color': '0x7f7f7f01',
#         'note_font_color': '0x7f7f7f01',
#         'header': '',
#         'subheader': '',
#         'contents': '',
#         'font_size': 'medium',
#         'preformatted': True,
#         'border_style': False,
#     }

#     # Set up panel
#     panel = nuke.Panel('Backdrop')
#     panel.addRGBColorChip('tile_color', settings.get('tile_color'))
#     panel.addRGBColorChip('note_font_color', settings.get('note_font_color'))
#     panel.addSingleLineInput('header', settings.get('header'))
#     panel.addSingleLineInput('subheader', settings.get('subheader'))
#     panel.addNotepad('contents', settings.get('contents'))
#     panel.addEnumerationPulldown('font_size', 'small medium large huge')
#     panel.addBooleanCheckBox('preformatted', settings.get('preformatted'))
#     panel.addBooleanCheckBox('border_style', settings.get('border_style'))
    
#     if not panel.show():
#         return None

#     # Get values from User
#     for item in settings.keys():
#         value = panel.value(item)
#         print 'settings: {0} to {1}'.format(item, value)
#         settings[item] = value

#     # Create backdrop node if one doesn't exist
#     if not node:
#         node = create_backdrop(settings)

#     # Apply settings to node
#     print settings