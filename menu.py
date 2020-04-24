import nuke
import sys


try:
    # Import all nuke python tools into the local namespace
    from nuketools import *

    # Import all nukepedia tools
    from nukepedia import *

    # drop.registerDropCallback()

except Exception as exc:
    sys.stderr.write('A problem loading tools occured...\n\n{0}'.format(exc))