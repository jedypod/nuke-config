import nuke
import os
import shutil
from os.path import dirname, join, isdir, isfile, expanduser

# Copy default files to the local artist directory 


# Copy default workspaces to the artist .nuke directory if they do not already exist
base_dir = dirname(__file__)
workspace_dir = join(dirname(base_dir), 'workspaces')
local_nuke_dir = expanduser('~/.nuke')
local_workspace_dir = join(local_nuke_dir, 'Workspaces/Nuke')

if not isdir(local_workspace_dir):
    os.makedirs(local_workspace_dir)

if isdir(workspace_dir):
    workspaces = os.listdir(workspace_dir)
    for workspace in workspaces:
        if workspace.endswith('.xml'):
            workspace_src_path = join(workspace_dir, workspace)
            workspace_dst_path = join(local_workspace_dir, workspace)
            if not isfile(workspace_dst_path):
                shutil.copy(workspace_src_path, local_workspace_dir)

# Create empty formats.tcl file to override default resolutions
formats_path = join(local_nuke_dir, 'formats.tcl')
if not isfile(formats_path):
    open(formats_path, 'a').close()