from __future__ import absolute_import
import nuke

# Set default Nuke preferences

# Suggested defaults that can be overriden by the artist
preferences_knobdefaults = {
        'platformPathRemaps': '',
        'colorPickerDefaultMode': '1',
        'UISequenceDisplayMode': r'Printf Notation (\%d)',
        'ShadeDAGNodes': 'false',
        'postage_stamp_mode': 'Static frame',
        'SnapToGrid': 'true',
        'show_grid': 'true',
        'OverlayColor': '0x1e1e1eff',
        'InputArrowSize': '18',
        'ArrowheadLength': '6',
        'ArrowheadWidth': '6',
        'ArrowWidth': '1',
        'rgb_only': 'true',
        'defaultBufferDepth': 'half-float',
        'defaultGPUForViewer': 'true',
        'defaultGPUForInputs': 'true',
        'dot_node_scale': '1',
        'Viewer3DControlEmulation': 'Maya',
        'UIRotoLineWidth': '0.5',
        'UIRotoDrawShadow': 'true',
        'scopesApplyViewerColorTransform': 'false',
        'scopesForceFullFrame': 'true',
        'defaultFlipbook': 'Flipbook Viewer',
}

# Forced defaults that cannot be persisted by the artist
preferences_forced = {
    'dot_node_scale': '1',
}


prefs = nuke.toNode('preferences')
for knob, val in list(preferences_knobdefaults.items()):
    nuke.knobDefault('preferences.{0}'.format(knob), val)

for knob, val in list(preferences_forced.items()):
    prefs[knob].setValue(val)
