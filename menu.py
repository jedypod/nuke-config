import nuke
import sys


# Import python tools
# This setup automatically imports all python files in the specified folders.
# Check the code in the __init__.py file inside each folder for how this is done.

try:
    # Tools written by jed
    from nuketools import *

    # Useful tools brought in from Nukepedia, mostly unchanged
    from nukepedia import *

    # Set up drop handler (not implemented yet)
    # drop.registerDropCallback()

except Exception as exc:
    # If there is an exception loading one of the tools
    # it will be handled and the error message will print
    sys.stderr.write('A problem loading tools occured...\n\n{0}'.format(exc))