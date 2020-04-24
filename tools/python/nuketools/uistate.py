import os
import nuke

try:
    from PySide2.QtCore import QSettings, QRect, QSize
except ImportError:
    from PySide.QtCore import QSettings, QRect, QSize

# Populate the uistate.ini file with some sane defaults.
# User overrides will stay in place
# https://support.foundry.com/hc/en-us/articles/360006950439-Q100538-How-to-set-default-values-for-knobs-and-preferences-stored-in-uistate-ini

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
setval('Nuke/startupWorkspace', 'floating-comp')

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