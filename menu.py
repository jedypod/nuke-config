import nuke

# Auto-imports all python modules inside nuketools folder
# Check the code in the __init__.py file for how this is done.
from nuketools import *


# Shortcut Editor gets imported last so it can override everything else.
import shortcuteditor
shortcuteditor.nuke_setup()

# Set up drop handler
# drop.registerDropCallback()