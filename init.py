import nuke
import os, errno


# The folder of this init.py file
base_path = os.path.dirname(__file__) 
pdirs = ['scripts']
for pdir in pdirs:
    nuke.pluginAddPath(os.path.join(base_path, pdir))


# Callbacks
#---------------------------------------------------------------------------------------------

# If a write directory does not exist, create it automatically.
def create_write_directory():
    directory = nuke.callbacks.filenameFilter(os.path.dirname(nuke.filename(nuke.thisNode())))
    if directory and not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except (OSError, e):
            if e.errno == 17:
                pass
nuke.addBeforeRender(create_write_directory)


# Works around bug in node.dependent calls which sometimes return an empty list in error
# Only add callback if not in commandline render mode
def eval_deps():
    nodes = nuke.allNodes()
    if nodes:
        _ = nodes[-1].dependent()
if '-X' not in nuke.rawArgs:
    nuke.addOnScriptLoad(eval_deps)