from __future__ import print_function
import nuke

nuke.menu('Nuke').addCommand('Render/Print Render Commands', 'print_render_commands.go(nuke.selectedNodes())', index=7)

def go(nodes):
    print('#!/usr/bin/bash')
    for n in nodes:
        print('{0} -X {1} -F {2} --cont -f {3}'.format(
            nuke.EXE_PATH, n.name(), n.frameRange(), nuke.root()['name'].getValue()))