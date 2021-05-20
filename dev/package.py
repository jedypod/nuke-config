name = 'nuke_config'

version = '2021.05.16.2340'

uuid = '9720C56A-15C9-4C1D-A70B-D34379C47C71'

author = 'Jed Smith'

help = 'https://github.com/jedypod/nuke-config'
description = "A portable, curated set of Nuke tools, preferences, scripts, and plugins to  increase efficiency and add functionality. This is intended as a powerful but simple off-the-shelf Nuke config. It mostly contains code and tools I've written, but there are also a few of the more exceptional Nukepedia tools included."

requires = [
    'nuke',
]

build_command = """
export root={root}/../
export prefix=$REZ_BUILD_INSTALL_PATH/nuke

mkdir -p $prefix

rsync -avp $root/{{tools,toolsets,workspaces,*.py}} $prefix
"""

def commands():
    env.NUKE_PATH.append('{root}/nuke')
    env.PYTHON_PATH.append('{root}/python')
