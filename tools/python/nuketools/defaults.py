import nuke
import os

# Defaults for many nodes that have the same knob value
knob_defaults = {
    'channels': {
        'rgb': [
                'Add',
                'ColorCorrect',
                'Grade',
                'Laplacian',
        ],
        'rgba': [
                'Blur',
                'BumpBoss',
                'Clamp',
                'Constant',
                'Defocus',
                'Dilate',
                'Dilate',
                'DirBlurWrapper',
                'EdgeBlur',
                'Emboss',
                'FilterErode',
                'Gamma',
                'Glint',
                'IDistort',
                'Invert',
                'Multiply',
                'Remove',
                'Roto',
                'Sharpen',
                'Soften',
                'VectorBlur',
                'ZBlur',
                'ZDefocus2',
                'ZSlice',
        ],
    }
}
for knob, vals in knob_defaults.iteritems():
    for val, nodes in vals.iteritems():
        for node in nodes:
            nuke.knobDefault('{0}.{1}'.format(node, knob), val)


# Presets for individual nodes that have multiple knob values
node_defaults = {
    'CheckerBoard': {'centerlinewidth': '0', },
    'ContactSheet': {
        'height': r'height/pixel_aspect*rows', 
        'roworder': 'TopBottom', 
        'width': r'width*columns', 
    },
    'Copy': {'bbox': 'union', 
        'from0': 'none', 
        'to0': 'none', 
        'crop': '0', 
    },
    'DeepCrop': {'bbox': '0 0 width height', },
    'Dot': {'note_font': 'Helvetica Bold', 'note_font_size': '24', 'note_font_color': '0xff'},
    'EdgeBlur': {'controlchannel': 'alpha', },
    'EXPTool': {'mode': 'Stops', },
    'Grade': {'black_clamp': '0', },
    'IDistort': {'uv': 'forward', },
    'Keymix': {'bbox': 'B side', },
    'LayerContactSheet': {'showLayerNames': '1', },
    'LensDistortion1_0': {'filter': 'Cubic', },
    'Merge2': {'bbox': 'B', },
    'Mirror': {'Horizontal': '1', },
    'Mirror2': {'flop': '1', },
    'OFlow2': {'timingOutputSpeed': '1', },
    'Read': {
        'after': 'hold',
        'auto_alpha': '1',
        'before': 'hold',
        'on_error': 'error',
        'tile_color': '2560137471',
    },
    'Remove': {'operation': 'keep', },
    'Retime': {
        'after': 'continue', 
        'before': 'continue', 
        'filter': 'none', 
    },
    'Root': {
        'colorManagement': 'OCIO', 
        'OCIO_config': 'custom', 
        'free_type_system_fonts': '0', 
        'lock_range': '1', 
        'project_directory': '[python {nuke.script_directory()}]', 
        'views_button': '0', 
    },
    'Roto': {
        'cliptype': 'no clip', 
        'output': 'rgba', 
    },
    'RotoPaint': {
        'brush_source':'3',
        'cliptype': 'no clip',
        'toolbox': '''clone { { brush ltt 2 h 0 } { clone ltt 2 h 0} { blur ltt 2} { sharpen ltt 2 h 0}{ smear ltt 2 h 0} { eraser ltt 2 h 0} { reveal ltt 2 h 0} { dodge ltt 2 h 0} { burn ltt 2 h 0} }''', 
    },
    'SoftClip': {
        'conversion': 'preserve hue and saturation',
        'softclip_max': '35', 
        'softclip_min': '8', 
    },
    'TimeBlur': {'shutteroffset': 'centred', },
    'Tracker4': {
        'adjust_for_luminance_changes': '0', 
        'autotracks_delete_keyframes': '0', 
        'autotracks_delete_keyframes_link': '0', 
        'create_key_on_move': '0', 
        'create_key_on_move_link': '0',
        'hide_progress_bar': '1', 
        'keyframe_display': '3', 
        'predict_track': '0', 
        'pretrack_filter': '2', 
        'retrack_on_move': '0', 
        'retrack_on_move_link': '0', 
        'show_error_on_track_link': '1', 
        'warp': '1', 
        'zoom_window_filter_behaviour': '0', 
        'zoom_window_size': '4', 
    },
    'Write': {
        '_jpeg_quality': '0.9', 
        'exr.metadata': '4', 
        'file_type': 'exr', 
        'write_gamma': '0', 
        'write_nclc': '0',
    },
    'ZDefocus2': {
        'math': 'depth', 
    }
}
for node, vals in node_defaults.iteritems():
    for knob, val in vals.iteritems():
        nuke.knobDefault('{0}.{1}'.format(node, knob), val)


# Global defaults for all knobs with the same name
defaults = {
    'postage_stamp': 'false',
    'shutteroffset': 'centred',
    'note_font': 'Helvetica',
}
for knob, val in defaults.iteritems():
    nuke.knobDefault(knob, val)


label_defaults = {
    'Colorspace': r'[value colorspace_in] -> [value colorspace_out]',
    'Dilate':'[value size]',
    'FilterErode':'[value size]',
    'FrameRange': '[knob first_frame]-[knob last_frame]',
    'OCIOColorSpace': r'[value in_colorspace] -> [value out_colorspace]',
    'OCIODisplay': '[value display]: [value view]',
    'OCIOFileTransform': '[file tail [value file]]\n[knob direction]',
    'OneView': r'[value view]',
    'Remove': r'[value operation]:\n[value channels]\n[value channels2]\n[value channels3]\n[value channels4]',
    'Retime': r'[value input.first] -> [value output.first]\noffset: [return [expr [value output.first]-[value input.first]]]\nspeed: [value speed]',
    'Shuffle': '',
    'TimeOffset': '[value time_offset]',
    'Vectorfield': '[file tail [value vfield_file]]',
}
for node, val in label_defaults.iteritems():
    nuke.knobDefault('{0}.label'.format(node), val)






# Add default favorite dirs
favorite_dirs = {
    'dev': '/cave/dev',
    'vault': '/cave/vault',
    'hdri': '/cave/vault/hdri',
    'stock': '/cave/vault/stock',
    'proj': '/cave/proj',
}

for name, path in sorted(favorite_dirs.items(), key=lambda (k, v): k):
    nuke.addFavoriteDir(name, path, nuke.IMAGE | nuke.SCRIPT | nuke.GEO | nuke.PYTHON)





# Set default formats
default_formats = [
    '854 480 1 SD_480p', 
    '960 540 1 SD_540p', 
    '1280 720 1 HD_720p', 
    '1920 1080 1 HD_1080p', 
    '3840 2160 1 UHD_4k', 
    '2048 1556 1 2K_Super_35_full-ap', 
    '1828 1556 2 2K_Cinemascope', 
    '2048 1080 1 2K_DCP', 
    '4096 3112 1 4K_Super_35_full-ap', 
    '3656 3112 2 4K_Cinemascope', 
    '4096 2160 1 4K_DCP', 
    '256 256 1 square_256', 
    '512 512 1 square_512', 
    '1024 1024 1 square_1K', 
    '2048 2048 1 square_2K', 
    '4096 4096 1 square_4K', 
    '1024 512 1 latlong_1k', 
    '2048 1024 1 latlong_2k', 
    '4096 2048 1 latlong_4k', 
    '8192 4096 1 latlong_8k', 
    '10240 5120 1 latlong_10k', 
    '12288 6144 1 latlong_12k', 
    '16384 8192 1 latlong_16k', 
]
for f in default_formats:
    nuke.addFormat(f)
nuke.knobDefault('root.format', '1920 1080 1 HD_1080p')
nuke.knobDefault('root.proxy_format', '960 540 1 SD_540p')








# Initialize uistate
# Populate the uistate.ini file with some sane defaults.
# User overrides will stay in place
# https://support.foundry.com/hc/en-us/articles/360006950439-Q100538-How-to-set-default-values-for-knobs-and-preferences-stored-in-uistate-ini

try:
    from PySide2.QtCore import QSettings, QRect, QSize
except ImportError:
    from PySide.QtCore import QSettings, QRect, QSize

settings = QSettings(os.path.expanduser('~/.nuke/uistate.ini'), QSettings.IniFormat)

def setval(key, value):
    # Set uistate key if it is not yet defined
    if settings.value(key):
        return
    else:
        settings.setValue(key, value)

# General
setval('askedAboutAnalyticsInVersion12', 'true')
setval('showSplashScreen', 'false')
setval('submitUsageStatistics', 'false')

# Nuke
setval('Nuke/startupWorkspace', 'comp_float')

# ColorPicker
# The sub-sections HSV RGB Swatches etc get converted to "\" when loaded in the uistate
setval('ColorPicker/Dynamic', 'true')
setval('ColorPicker/ShownColorSpaces/HSV', 'true')
setval('ColorPicker/ShownColorSpaces/RGB', 'true')
setval('ColorPicker/ShownColorSpaces/Swatches', 'false')
setval('ColorPicker/ShownColorSpaces/TMI', 'true')
setval('ColorPicker/ShownColorSpaces/Wheel', 'true')

# WindowLocations
# Has to be a QRect object, which gets translated to @Rect() in the uistate
setval('WindowLocations/ColorPicker', QRect(621, 574, 1041, 370))

# scripteditor
setval('scripteditor/SaveAndLoadHistory', 'true')

# FileBrowser
setval('FileBrowser/preview', 'true')
setval('FileBrowser/size', QSize(1050, 1050))