import nuke
import os, errno


# Nuke version number
# nuke_version = float(str(nuke.NUKE_VERSION_MAJOR) + '.' + str(nuke.NUKE_VERSION_MINOR))

# The folder of this init.py file
base_path = os.path.dirname(__file__)
plugin_dirs = ['tools']
# Add plugin_dirs and subdirs to plugin path
for plugin_dir in plugin_dirs:
    fullpath = os.path.join(base_path, plugin_dir)
    nuke.tprint('Loading plugin directory: {0}'.format(fullpath))
    if os.path.isdir(fullpath):
        nuke.pluginAddPath(fullpath)
        subdirs = [d for d in os.listdir(fullpath) if os.path.isdir(os.path.join(fullpath, d))]
        for subdir in subdirs:
            nuke.pluginAddPath(os.path.join(fullpath, subdir))


# Callbacks
#---------------------------------------------------------------------------------------------

# If a write directory does not exist, create it automatically.
def create_write_directory():
    directory = nuke.callbacks.filenameFilter(os.path.dirname(nuke.filename(nuke.thisNode())))
    if directory and not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError, e:
            if e.errno == 17:
                pass
nuke.addBeforeRender(create_write_directory)


# Works around bug in node.dependent calls which sometimes return an empty list in error
def eval_deps():
    nodes = nuke.allNodes()
    if nodes:
        _ = nodes[-1].dependent()
if '-X' not in nuke.rawArgs:
    nuke.addOnScriptLoad(eval_deps)