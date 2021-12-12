from __future__ import division
from __future__ import print_function

import nuke
import nukescripts
import operator, math, os
import string
import random


# Utilities for enhancing efficiency when interacting with Nuke's Directed Acyclic Graph

# Viewer Shortcuts
nuke.menu('Viewer').addCommand('Next Frame', 'nuke.activeViewer().frameControl(1)', 'shift+f', shortcutContext=0)
nuke.menu('Viewer').addCommand('Previous Frame', 'nuke.activeViewer().frameControl(-1)', 'shift+d', shortcutContext=0)
nuke.menu('Viewer').addCommand('Next Keyframe', 'nuke.activeViewer().frameControl(2)', 'alt+shift+f', shortcutContext=0)
nuke.menu('Viewer').addCommand('Previous Keyframe', 'nuke.activeViewer().frameControl(-2)', 'alt+shift+d', shortcutContext=0)
nuke.menu('Viewer').addCommand('Next Frame', 'nuke.activeViewer().frameControl(1)', 'shift+f', shortcutContext=0)
nuke.menu('Viewer').addCommand('Play Forward', 'nuke.activeViewer().frameControl(5)', 'ctrl+alt+f', shortcutContext=0)
nuke.menu('Viewer').addCommand('Play Backward', 'nuke.activeViewer().frameControl(-5)', 'ctrl+alt+d', shortcutContext=0)
nuke.menu('Viewer').findItem('Show Overscan').setShortcut('alt+shift+o')



# Register keyboard shortcuts and menu entries
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Right', 'dag.move(1, 0, norm=False)', 'alt+meta+Right')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Left', 'dag.move(-1, 0, norm=False)', 'alt+meta+Left')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Up', 'dag.move(0, -1, norm=False)', 'alt+meta+Up')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Down', 'dag.move(0, 1, norm=False)', 'alt+meta+Down')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Right Big', 'dag.move(4, 0)', 'alt+meta+shift+Right')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Left Big', 'dag.move(-4, 0)', 'alt+meta+shift+Left')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Up Big', 'dag.move(0, -4)', 'alt+meta+shift+Up')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Down Big', 'dag.move(0, 4)', 'alt+meta+shift+Down')

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Up Vertical', 'dag.scale(1, 2)', 'meta+shift++', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Down Vertical', 'dag.scale(1, 0.5)', 'meta+shift+_', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Up Horizontal', 'dag.scale(0, 2)', 'meta+=', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Down Horizontal', 'dag.scale(0, 0.5)', 'meta+-', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Mirror Horizontal from Right', 'dag.scale(0, -1, pivot="min")', 'meta+m')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Mirror Horizontal from Left', 'dag.scale(0, -1, pivot="max")', 'meta+shift+m')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Mirror Vertical from Top', 'dag.scale(1, -1, pivot="max")', 'ctrl+meta+alt+m')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Mirror Vertical from Bottom', 'dag.scale(1, -1, pivot="min")', 'ctrl+alt+meta+shift+m')

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Left', 'dag.align("left")', 'ctrl+shift+left', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Right', 'dag.align("right")', 'ctrl+shift+right', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Up', 'dag.align("up")', 'ctrl+shift+up', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Down', 'dag.align("down")', 'ctrl+shift+down', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Snap to Grid', 'dag.snap_to_grid()', 'alt+s', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Connect Selected to Closest', 'dag.connect_to_closest()', 'meta+shift+y', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Connect Closest to Selected', 'dag.connect_to_closest(direction=1)', 'alt+meta+shift+y', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Paste To Selected', 'dag.paste_to_selected()', 'alt+v', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Read from Write', 'dag.read_from_write()', 'alt+r', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar Class', 'nuke.selectSimilar(nuke.MATCH_CLASS)', 'alt+meta+shift+s', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar Color', 'nuke.selectSimilar(nuke.MATCH_COLOR)', 'alt+meta+shift+c', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar Y Position', 'dag.select_similar_position(axis=1)', 'alt+meta+shift+v', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar X Position', 'dag.select_similar_position(axis=0)', 'ctrl+alt+meta+shift+v', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Upstream', 'dag.select_upstream(nuke.selectedNodes())', 'alt+meta+shift+u', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Invert Selection', 'nuke.invertSelection()', 'alt+meta+shift+i', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Connected Nodes', 'dag.select_connected(nuke.selectedNodes())', 'alt+meta+shift+o', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Downstream', 'dag.select_downstream(nuke.selectedNodes())', 'alt+meta+shift+p', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Unused Nodes', 'dag.select_unused(nuke.selectedNodes())', 'ctrl+alt+meta+shift+u', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Properties Panel Open', 'dag.open_panels()', 'a', shortcutContext=1)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Properties Panel Open and Persist', 'dag.open_panels(persist=True)', 'meta+a', shortcutContext=1)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Properties Panel Close', 'dag.close_panels()', 'alt+a', shortcutContext=1)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Properties Panel Close and UnPersist', 'dag.close_panels(unpersist=True)', 'alt+shift+a', shortcutContext=1)

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Sort By File Knob', 'dag.auto_place()', 'l', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Node/Declone', 'dag.declone_nodes(nuke.selectedNodes())', 'alt+shift+k', shortcutContext=2)
nuke.menu('Nuke').addCommand('File/Export Selected with Root Settings', 'dag.export_selected_nodes()', 'ctrl+shift+e', index=7)
nuke.menu('Nuke').addCommand('File/Import Script', 'nukescripts.import_script()', 'ctrl+shift+i', index=8)


nuke.menu('Nuke').addCommand('Edit/Node/Swap A - B', 'dag.swap_node()', 'shift+x')
nuke.menu('Viewer').addCommand("Swap View", "dag.swap_view()", "shift+q")

nuke.menu('Nodes').addCommand( 'Transform/Transform', 'dag.create_transform()', 't')

nuke.menu('Nodes').addCommand('Other/Create Dots', 'dag.create_dots()', 'alt+d', shortcutContext=2)
nuke.menu('Nodes').addCommand('Other/Create Dots Branched', 'dag.create_dots(branch=True)', 'alt+shift+d', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Desat Backdrops', 'for bd in nuke.allNodes("BackdropNode"): bd["tile_color"].setValue(0x191919ff)')


# DAG Position Commands
nuke.menu('Nuke').addCommand('Edit/Bookmark/Restore Position 1', 'nukescripts.bookmarks.quickRestore(1)', 'ctrl+1', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Restore Position 2', 'nukescripts.bookmarks.quickRestore(2)', 'ctrl+2', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Restore Position 3', 'nukescripts.bookmarks.quickRestore(3)', 'ctrl+3', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Restore Position 4', 'nukescripts.bookmarks.quickRestore(4)', 'ctrl+4', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Restore Position 5', 'nukescripts.bookmarks.quickRestore(5)', 'ctrl+5', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Restore Position 6', 'nukescripts.bookmarks.quickRestore(6)', 'ctrl+6', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Save Position 1', 'nukescripts.bookmarks.quickSave(1)', 'ctrl+shift+1', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Save Position 2', 'nukescripts.bookmarks.quickSave(2)', 'ctrl+shift+2', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Save Position 3', 'nukescripts.bookmarks.quickSave(3)', 'ctrl+shift+3', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Save Position 4', 'nukescripts.bookmarks.quickSave(4)', 'ctrl+shift+4', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Save Position 5', 'nukescripts.bookmarks.quickSave(5)', 'ctrl+shift+5', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Bookmark/Save Position 6', 'nukescripts.bookmarks.quickSave(6)', 'ctrl+shift+6', shortcutContext=2)

# # Hlink Nodes
# nuke.menu('Nuke').addCommand('Edit/HLink Cut', 'dag.hlink_cut()', 'ctrl+x')
# nuke.menu('Nuke').addCommand('Edit/HLink Copy', 'dag.hlink_copy()', 'ctrl+c')
# nuke.menu('Nuke').addCommand('Edit/HLink Paste', 'dag.hlink_paste()', 'ctrl+v')
# nuke.menu('Nuke').addCommand('Edit/HLink Create', 'dag.hlink_create()', 'alt+shift+p')
# nuke.menu('Nuke').addCommand('Edit/Paste', 'nuke.nodePaste("%clipboard%")', 'ctrl+shift+v', index=6)

nuke.menu('Nodes').addCommand('Other/Create Pointer', 'dag.create_pointer()', 'alt+t')







# Get the grid size from the preferences. Used as the default unit of movement.
grid = (int(nuke.toNode('preferences').knob('GridWidth').value()), int(nuke.toNode('preferences').knob('GridHeight').value()))


def unselect(nodes=None):
    # Unselect nodes
    if not nodes:
        nodes = nuke.allNodes(recurseGroups=True)
    if not isinstance(nodes, list):
        return
    _ = [n.setSelected(False) for n in nodes]


def select(nodes):
    # Select specified nodes
    if not isinstance(nodes, list):
        return
    _ = [n.setSelected(True) for n in nodes]


def get_parent(node):
    # return node's parent node, return nuke.root() if on the top level
    return nuke.toNode('.'.join(node.fullName().split('.')[:-1])) or nuke.root()


def get_topnode(node):

    # return the topnode of node
    return nuke.toNode(nuke.tcl('return [value [topnode {0}].name]'.format(node.fullName())))


def get_pos(node):
    # return 2d list of centered node positions
    if node.Class() == 'BackdropNode':
        return [node.xpos(), node.ypos()]
    else:
        return [node.xpos() + node.screenWidth()/2, node.ypos() + node.screenHeight()/2]


def set_pos(node, posx, posy):
    # Set node's position given a centered position based on screen width
    # param: pos - 2dim list of int node positions
    if node.Class() == 'BackdropNode':
        return node.setXYpos(int(posx), int(posy))
    else:
        return node.setXYpos(int(posx - node.screenWidth()/2), int(posy - node.screenHeight()/2))


def hide_panel():
    # Always hide control panels on node creation if node not in exceptions
    node = nuke.thisNode()
    exceptions = ['Roto', 'RotoPaint', 'Bezier']
    if node.Class() not in exceptions:
        nuke.thisNode().showControlPanel()
        nuke.thisNode().hideControlPanel()
nuke.addOnUserCreate(hide_panel)


def open_panels(nodes=None, persist=False):
    # Open properties panels
    if not nodes:
        nodes = nuke.selectedNodes()
    ignored = ['Viewer']
    if len(nodes) > 10:
        if not nuke.ask('Continuing will open {0} properties panels. \nAre you sure you want to continue?'.format(len(nodes))):
            return
    if persist:
        for n in nodes:
            l = n['label']
            lv = l.getValue()
            if not lv.endswith('__persist'):
                l.setValue((lv + '__persist'))
    for node in nodes:
        if node.Class() not in ignored:
            # if node.shown():
            #     if nclass in buggy:
            #         # There is a bug with node.shown() for some node classes, where .shown()
            #         # incorrectly returns true if it is hidden. Workaround by cutting node and undoing
            #         nuke.Undo().begin()
            #         nuke.delete(node)
            #         nuke.Undo().end()
            #         nuke.undo()
            #         node.setSelected(True)
            #     node.hideControlPanel()
            # else:
            node.showControlPanel()


def close_panels(nodes=None, unpersist=False):
    # Close all properties panels
    if not nodes:
        nodes = nuke.allNodes(recurseGroups=True)
    for node in nodes:
        persisted = node['label'].getValue().endswith('__persist')
        if unpersist:
            # close all panels and unpersist nodes 
            node.hideControlPanel()
            if persisted:
                node['label'].setValue((node['label'].getValue().replace('__persist', '')))
        else:
            # close all non-persisted nodes
            if persisted:
                continue
            node.hideControlPanel()

            node.hideControlPanel()
        


def select_similar_position(axis=1):
    nodes = nuke.selectedNodes()
    if not nodes:
        return
    node = nodes[0]
    prev_selected = nodes[1:]
    threshold = 1
    unselect()
    select(prev_selected)
    if axis:
        same_pos_nodes = {n:n.xpos() for n in nuke.allNodes() if abs(n.ypos()- node.ypos()) < threshold}
    else:
        same_pos_nodes = {n:n.ypos() for n in nuke.allNodes() if abs(n.xpos()- node.xpos()) < threshold}
    sorted_nodes = sorted(list(same_pos_nodes.items()), key=operator.itemgetter(1))
    for n, pos in sorted_nodes:
        n.setSelected(True)


def snap_to_grid():
    # Snap selected nodes to grid
    nodes = nuke.selectedNodes()
    for node in nodes:
        nuke.autoplaceSnap(node)


def auto_place():
    # autoplace all selected
    nodes = nuke.selectedNodes()

    # Sort by file knob value if the nodes have one
    filenodes = {n: n['file'].getValue() for n in nodes if 'file' in n.knobs()}
    if filenodes:
        sorted_filenodes = sorted(list(filenodes.items()), key=operator.itemgetter(1))
        filenodes_pos = {n: [n.xpos(), n.ypos()] for n in nodes if 'file' in n.knobs()}
        ypos_sort = sorted(list(filenodes_pos.items()), key=lambda k_v: k_v[1][1])
        xpos_sort = sorted(list(filenodes_pos.items()), key=lambda k_v1: k_v1[1][0])
        start_pos = [xpos_sort[0][1][0], ypos_sort[0][1][1]]
        for node, filepath in sorted_filenodes:
            node.setXYpos(start_pos[0], start_pos[1])
            start_pos = (start_pos[0] + grid[0]*2, start_pos[1])

    # Normal autoplace for nodes without file knob
    normal_nodes = [n for n in nodes if 'file' not in n.knobs()]
    unselect()
    _ = [n.setSelected(True) for n in normal_nodes]
    nuke.autoplace_all()
    _ = [n.setSelected(True) for n in nodes]


def move(xvel, yvel, norm=True):
    # Move selected nodes by specified number of grid lengths in x and y
    nodes = nuke.selectedNodes()
    if norm: yvel *= 2
    for node in nodes:
        node.setXYpos(int(node.xpos() + grid[0] * xvel), int(node.ypos() + grid[1] * yvel))


def get_closest_node(node):
    # Return the closest node to node
    distances = {}
    for n in nuke.allNodes():
        if n.name() == node.name():
            continue
        distance = math.sqrt( 
            math.pow( (node.xpos() - n.xpos()), 2 ) + math.pow( (node.ypos() - n.ypos()), 2 )
        )
        distances[n.name()] = distance
    return nuke.toNode(min(distances, key=distances.get))


def connect_to_closest(direction=0):
    # Connect next available input of all selected nodes to the closest node
    for node in nuke.selectedNodes():
        closest = get_closest_node(node)
        if direction:
            closest.setInput(0, node)
        else:
            node.connectInput(0, closest)


def paste_to_selected():
    nodes = nuke.selectedNodes()
    all_nodes = nuke.allNodes()
    unselect()
    for node in nodes:
        node.setSelected(True)
        nuke.nodePaste('%clipboard')
        unselect()
    if not nodes:
        nuke.nodePaste('%clipboard')
    # Select pasted nodes
    select(all_nodes)
    nuke.invertSelection()
    

def align(direction):
    # Align nodes to the farthest outlier in the specified direction.
    # param: direction - one of: left | right | up | down

    nodes = nuke.selectedNodes()

    if len(nodes) < 2:
        return

    horizontally = ['left', 'right']
    vertically = ['up', 'down']

    if direction in horizontally:
        align = 0
    elif direction in vertically:
        align = 1
    else:
        print('Error: invalid direction specified: {0}'.format(direction))
        return

    positions = {n: get_pos(n) for n in nodes}
    sorted_positions = sorted(list(positions.items()), key=lambda k_v2: k_v2[1][align])
    if direction in ['down', 'right']:
        sorted_positions.reverse()
    target = sorted_positions[0]
    target_pos = target[1]

    offset = 0

    other_axis = abs(1 - align)

    sorted_other_axis = sorted(list(positions.items()), key=lambda k_v3: k_v3[1][other_axis])

    nuke.Undo().begin()
    for i in range(len(sorted_other_axis)):
        node = sorted_other_axis[i][0]
        pos = sorted_other_axis[i][1]
        if i == 0: 
            distance = 0
            overlapping = False
            prev_pos = pos
        else:
            prev_pos = sorted_other_axis[i-1][1]
            # Compare current node position to previous node position.
            # If difference is < overlap threshold, nodes are overlapping.
            distance = abs(pos[other_axis] + grid[other_axis] * offset - prev_pos[other_axis])
            overlap_threshold = [int(node.screenWidth() * 1.1), int(node.screenHeight() * 1.1)]
            overlapping = distance < overlap_threshold[other_axis]

        if overlapping:
            offset += 1

        new_pos = pos
        new_pos[other_axis] = int(pos[other_axis] + grid[other_axis] * offset)

        # Set value into sorted_other_axis also so we access the right value on the next loop
        sorted_other_axis[i][1][other_axis] = new_pos[other_axis]
        
        if align:
            set_pos(node, new_pos[other_axis], target_pos[align])
        else:
            set_pos(node, target_pos[align], new_pos[other_axis])
        i += 1
    nuke.Undo().end()


def scale(axis, scale, pivot='max'):
    # Scale selected nodes by factor of xscale, yscale
    # param: axis - one of 0 or 1 - x or y scale
    # param: float scale - factor to scale. 1 will do nothing. 2 will scale up 1 grid unit.
    # param: str pivot - where to scale from. One of min | max | center
    pivots = ['min', 'max', 'center']
    if pivot not in pivots:
        return
    nodes = nuke.selectedNodes()
    if len(nodes) < 2:
        return

    positions = {n: get_pos(n) for n in nodes}
    sort = sorted(list(positions.items()), key=lambda k_v4: k_v4[1][axis])

    minpos = sort[0][1][axis]
    maxpos = sort[-1][1][axis]

    if pivot == 'max':
        pivot_pos = maxpos
    elif pivot == 'min':
        pivot_pos = minpos
    elif pivot == 'center':
        pivot_pos = (minpos - maxpos)/2 + minpos

    nuke.Undo().begin()
    for node, pos in positions.items():
        if axis:
            new_pos = (pos[1] - pivot_pos) * scale + pivot_pos
            set_pos(node, pos[0], new_pos)
            if node.Class() == 'BackdropNode':
                bdpos = ((pos[1] + node['bdheight'].getValue()) - pivot_pos) * scale + pivot_pos - node.ypos()

                if scale > 0:
                    node['bdheight'].setValue(bdpos)
                else:
                    node.setXYpos(pos[0], int(new_pos-abs(bdpos)))
        else:
            new_pos = (pos[0] - pivot_pos) * scale + pivot_pos
            set_pos(node, new_pos, pos[1])
            if node.Class() == 'BackdropNode':
                bdpos = ((pos[0] + node['bdwidth'].getValue()) - pivot_pos) * scale + pivot_pos - node.xpos()
                if scale > 0:
                    node['bdwidth'].setValue(bdpos)
                else:
                    node.setXYpos(int(new_pos-abs(bdpos)), int(node.ypos()))
    nuke.Undo().end()



def copy_inputs(src, dst):
    # copy input connections from src node to dst node
    # number of inputs must be the same between nodes
    for j in range(dst.inputs()):
        dst.setInput(j, None)
    for i in range(src.inputs()):
        dst.setInput(i, src.input(i))


def declone(node):
    # Declone a single node
    if not node.clones():
        return
    parent = get_parent(node)
    parent.begin()
    node.setSelected(True)
    args = node.writeKnobs( nuke.WRITE_ALL | nuke.WRITE_USER_KNOB_DEFS |
                            nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_SCRIPT)
    decloned_node = nuke.createNode(node.Class(), knobs=args, inpanel=False)
    copy_inputs(node, decloned_node)
    nuke.delete(node)
    parent.end()
    return decloned_node


def declone_nodes(nodes):
    # A better declone than the buggy default nukescripts.misc.declone()
    unselect()
    decloned_nodes = list()
    for node in nodes:
        decloned_nodes.append(declone(node))
    if decloned_nodes:
        # Restore selection
        _ = [n.setSelected(True) for n in decloned_nodes]


def export_selected_nodes():
    path = nuke.getFilename("Export Selected To:")
    if not path:
        return
    nuke.nodeCopy(path)
    root = nuke.root()
    rootstring = root.writeKnobs(nuke.TO_SCRIPT | nuke.WRITE_USER_KNOB_DEFS)
    rootstring = "%s\nfirst_frame %d\nlast_frame %d" % (rootstring, root['first_frame'].value(), root['last_frame'].value())
    rootstring = "%s\nproxy_format \"%s\"" % (rootstring, root['proxy_format'].toScript())
    rootstring = "Root {\n%s\n}" % rootstring
    noroot = open(path).read()
    with open(path, "w+") as f:
        f.write((rootstring + "\n" + noroot))



#--------------------------------------------------------------
# Nuke Node Dependency Utilities
if nuke.NUKE_VERSION_MAJOR > 11:
    connection_filter = nuke.INPUTS | nuke.HIDDEN_INPUTS | nuke.EXPRESSIONS | nuke.LINKINPUTS
else:
    connection_filter = nuke.INPUTS | nuke.HIDDEN_INPUTS | nuke.EXPRESSIONS

def find_root_nodes(node, results=[], remove_roots_with_inputs=True):
    # Find all root nodes of node. 
    # If remove_roots_with_inputs: remove root nodes with an input (like Roto etc)
    for dependency in node.dependencies():
        if not dependency.dependencies():
            results.append(dependency)
        else:
            find_root_nodes(dependency, results)
    if remove_roots_with_inputs:
        results = [res for res in results if res.maxInputs() == 0]
    return results


def upstream(node, max_depth=-1, deps=set([])):
    if max_depth != 0:
       new_deps = set([n for n in nuke.dependencies(node, what=connection_filter) if n not in deps])
       deps |= new_deps
       for dep in new_deps:
          upstream(dep, max_depth-1, deps)
    return deps


def connected(nodes, upstream=True, downstream=True):
    # return all upstream and/or downstream nodes of node
    # based on nuke.overrides.selectConnectedNodes()
    all_deps = set()
    deps_list = nodes
    evaluate_all = True
    while deps_list:
        deps = []
        if upstream:
            deps += nuke.dependencies(deps_list, connection_filter)
        if downstream:
            deps += nuke.dependentNodes(connection_filter, deps_list, evaluate_all)
        evaluate_all = False
        deps_list = [d for d in deps if d not in all_deps and not all_deps.add(d)]
    return all_deps

def select_upstream(nodes):
    # Select all upstream dependencies of node
    deps = [n for n in connected(nodes, upstream=True, downstream=False)]
    select(deps)
    return deps

def select_downstream(nodes):
    # Select all downstream dependencies of node
    deps = [n for n in connected(nodes, upstream=False, downstream=True)]
    select(deps)
    return deps

def select_connected(nodes):
    # Select all nodes connected to node
    deps = [n for n in connected(nodes, upstream=True, downstream=True)]
    select(deps)
    return deps

def select_unused(nodes):
    # select all nodes that are not upstream or downstream of :param: nodes
    # Backdrops and dot nodes with a label are omitted.
    connected_nodes = [n for n in connected(nodes, upstream=True, downstream=True)]
    unused_nodes = [n for n in nuke.allNodes() if n not in connected_nodes and n.Class() != 'BackdropNode' and not (n.Class() == 'Dot' and n['label'].getValue())]
    unselect()
    select(unused_nodes)
    return unused_nodes






# DAG Positions
# Inspired by Simon Bjork's sb_dagPosition.py https://www.bjorkvisuals.com/tools/the-foundrys-nuke/python
# Using built-in nukescripts.bookmarks module now instead.
def save_dag_pos(preset):
    # Save current dag zoom and position as a preset on the active viewer
    zoom = nuke.zoom()
    pos = nuke.center()
    viewer = nuke.activeViewer()
    if not viewer:
        nuke.message('Error: please create a viewer to store the dag positions on...')
        return
    else:
        viewer = viewer.node()
    if 'dagpos' not in viewer.knobs():
        viewer.addKnob(nuke.String_Knob('dagpos', 'dagpos', '0,0,0:0,0,0:0,0,0:0,0,0:0,0,0:0,0,0:0,0,0:0,0,0:0,0,0:0,0,0'))
        dagpos_knob = viewer['dagpos']
        dagpos_knob.setFlag(nuke.STARTLINE)
        dagpos_knob.setEnabled(False)
    else:
        dagpos_knob = viewer['dagpos']
    dagpos_vals = dagpos_knob.getValue().split(':')
    dagpos_vals.pop(preset-1)
    new_dagpos = ','.join([str(zoom), str(pos[0]), str(pos[1])])
    dagpos_vals.insert(preset-1, new_dagpos)
    dagpos_knob.setValue(':'.join(dagpos_vals))

def load_dag_pos(preset):
    # Load dag zoom and position from specified preset number
    viewer = nuke.activeViewer()
    if not viewer:
        nuke.message('Error: please create a viewer to store the dag positions on...')
        return
    viewer = viewer.node()
    if 'dagpos' not in viewer.knobs():
        nuke.message('No preset positions created yet...')
        return
    dagpos_knob = viewer['dagpos']
    dagpos_vals = dagpos_knob.getValue().split(':')[preset-1]
    zoom, xpos, ypos = dagpos_vals.split(',')
    nuke.zoom(float(zoom), [float(xpos), float(ypos)])




#----------------------------------------------------------------------------------
# Hidden Input Link Nodes
# This is no longer used in favor of the anchor / pointer workflow

def hidden_inputs_in_selection(nodes):
    return [n for n in nodes if 'hide_input' in n.knobs() and n['hide_input'].getValue()]

def set_hlink_knobs(nodes):
    # Add knob to track what node this node is connected to
    for node in hidden_inputs_in_selection(nodes):
        if not 'hlink_node' in node.knobs():
            node.addKnob(nuke.String_Knob('hlink_node', 'hlink_node'))
        input_node = node.input(0)
        if input_node:
            node['hlink_node'].setValue(input_node.fullName())
        else:
            node['hlink_node'].setValue('')

def hlink_copy():
    nodes = nuke.selectedNodes()
    if nodes:
        set_hlink_knobs(nodes)
        nuke.nodeCopy('%clipboard%')

def hlink_cut():
    hlink_copy()
    nukescripts.node_delete(popupOnError=True)

def hlink_paste():
    nuke.nodePaste('%clipboard%')
    for node in hidden_inputs_in_selection(nuke.selectedNodes()):
        if 'hlink_node' in node.knobs():
            target = nuke.toNode(node['hlink_node'].getValue())
            if target:
                node.setInput(0, target)

def hlink_create():
    # Creates an hlink node for each selected node
    nodes = nuke.selectedNodes()
    unselect()
    hlinks = []
    for node in nodes:
        hlink = nuke.createNode('Dot', 'hide_input 1 note_font_size 18', inpanel=False)
        hlinks.append(hlink)
        hlink.setInput(0, node)
        target_name = node.fullName()
        set_hlink_knobs([hlink])
        hlink['hlink_node'].setValue(target_name)
        label = hlink['label']
        target_label = node['label'].getValue()
        if node.Class() == 'Read':
            label.setValue(' | ' + node['label'].getValue() + '\n' + os.path.basename(node['file'].getValue()))
        elif target_label:
            label.setValue(' | ' + target_label)
        else:
            label.setValue(' | ' + target_name)
        hlink.setXYpos(node.xpos() - grid[0]*2, node.ypos()-grid[1]*0)
        nuke.autoplaceSnap(hlink)
    _ = [n.setSelected(True) for n in hlinks]



def dec2hex(dec):
    hexcol = '%08x' % dec
    return '0x%02x%02x%02x' %  (int(hexcol[0:2], 16), int(hexcol[2:4], 16), int(hexcol[4:6], 16))



def create_pointer():
    # Create an anchor / pointer set
    
    # Customization Options
    # Node class to use for anchor / pointer nodes. Defaults to NoOp but could be a Dot node if you prefer
    AP_CLASS = 'NoOp'   

    # Displays an input / output icon on the node to visually differentiate it from the standard node class
    AP_ICON = True



    nodes = nuke.selectedNodes()
    if not nodes:
        return

    for target in nodes:
        upstream = [n for n in connected(nodes, upstream=True, downstream=False)]

        if len(upstream) > 5:
            if not nuke.ask('More than 5 upstream nodes. Are you sure you want to continue?'):
                return

        randstr = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
        
        topnode = get_topnode(target)

        target_label = target['label'].getValue()

        # If topnode has a file knob, use that to set title
        # If it's a roto node, use the roto label
        if 'file' in topnode.knobs():
            pointer_title = os.path.basename(topnode['file'].getValue())
            if '.' in pointer_title:
                pointer_title = pointer_title.split('.')[0]
        elif topnode.Class() in ['Roto', 'RotoPaint'] and topnode['label'].getValue():
            pointer_title = topnode['label'].getValue()
        elif target_label:
            pointer_title = target_label
        else:
            pointer_title = ''

        topnode_color = topnode['tile_color'].value()

        if topnode_color == 0:
            # Get default color from prefs if node is not colored https://community.foundry.com/discuss/topic/103301/get-the-default-tile-color-from-preferences
            prefs = nuke.toNode('preferences')
            default_colors = {prefs['NodeColour{0:02d}Color'.format(i)].value(): prefs['NodeColourClass{0:02d}'.format(i)].value() for i in range(1, 14)}
            node_class = topnode.Class().lower()
            node_class = ''.join([i for i in node_class if not i.isdigit()])
            for color, classes in list(default_colors.items()):
                if node_class in classes:
                    topnode_color = color
                    break
            if 'deep' in node_class:
                topnode_color = prefs['NodeColourDeepColor'].value()
        
        if len(nodes) == 1:
            # Only prompt the user for info if there is one selected node
            panel = nuke.Panel('Create Pointer')
            panel.addSingleLineInput('title', pointer_title)
            if panel.show():
                pointer_title = panel.value('title')
            else:
                return

        has_downstream = len(select_downstream(target)) > 0
        unselect()

        if not has_downstream:
            target.setSelected(True)

        # create anchor node
        anchor = nuke.createNode(AP_CLASS, 'name ___anchor_{0}{1}label "<font size=6>\[value title]" note_font_color 0x999999ff'.format(
            randstr, ' icon Output.png ' if AP_ICON else ' '))
        anchor.addKnob(nuke.Tab_Knob('anchor_tab', 'anchor'))
        anchor.addKnob(nuke.String_Knob('title', 'title'))
        anchor['title'].setValue(pointer_title)
        anchor['tile_color'].setValue(topnode_color)
        anchor.setInput(0, target)
        anchor.setSelected(True)

        # create pointer node
        pointer = nuke.createNode(AP_CLASS, 'name ___pointer_{0} hide_input true{1} note_font_color 0x999999ff'.format(
            randstr, ' icon Input.png ' if AP_ICON else ''))
        pointer.addKnob(nuke.Tab_Knob('pointer_tab', 'pointer'))
        pointer.addKnob(nuke.String_Knob('target', 'target'))
        pointer['target'].setValue(anchor.fullName())
        pointer['label'].setValue('<font size=7> [if {[exists input.title]} {return [value input.title]}]')
        pointer.addKnob(nuke.PyScript_Knob('connect_to_target', 'connect'))
        pointer['connect_to_target'].setFlag(nuke.STARTLINE)
        pointer.addKnob(nuke.PyScript_Knob('zoom_to_target', 'zoom'))
        pointer.addKnob(nuke.PyScript_Knob('set_target', 'set target'))
        pointer['connect_to_target'].setValue('''n = nuke.thisNode()
t = n['target'].getValue()
if nuke.exists(t):
    tn = nuke.toNode(t)
    n.setInput(0, tn)''')
        pointer['zoom_to_target'].setValue('''t = nuke.thisNode()['target'].getValue()
if nuke.exists(t):
    tn = nuke.toNode(t)
    nuke.zoom(2.0, [tn.xpos(), tn.ypos()])''')
        pointer['set_target'].setValue('''n = nuke.thisNode()
sn = nuke.selectedNodes()
if sn:
    t = sn[-1]
n['target'].setValue(t.fullName())''')
        # set autolabel knob to execute python script to reconnect node to target.
        # it's a hack but it works to automatically reconnect the input without using knobChanged callbacks!
        # FYI, onCreate callback can not connect input 0 due to a nuke bug
        pointer['autolabel'].setValue('"{0}\\n{1}".format(nuke.thisNode().name(), nuke.thisNode()["label"].evaluate()) if nuke.thisNode().setInput(0, nuke.toNode(nuke.thisNode()["target"].getValue())) else ""')
        pointer.setXYpos(anchor.xpos(), anchor.ypos()+120)
        pointer['tile_color'].setValue(topnode_color)


def create_dots(branch=False):
    # Create dot nodes
    nodes = nuke.selectedNodes()
    dots = list()
    for node in nodes:
        unselect()
        pos = get_pos(node)
        if not branch:
            select([node])
        dot = nuke.createNode('Dot', inpanel=False)
        if branch:
            set_pos(dot, pos[0] + grid[0], pos[1])
            dot.setInput(0, node)
        else:
            set_pos(dot, pos[0], pos[1] + grid[1]*2)
        dots.append(dot)
        unselect(dot)
    select(dots)
    if not nodes:
        dot = nuke.createNode('Dot', inpanel=False)



def create_transform():
    # Create a Transform or TransformGeo node depending on node type
    nodes = nuke.selectedNodes()
    if not nodes:
        nuke.createNode('Transform')
        return
    unselect()
    transform_nodes = list()
    for node in nodes:
        node.setSelected(True)
        if 'render_mode' in node.knobs():
            new_node = nuke.createNode('TransformGeo')
            if new_node:
                transform_nodes.append(new_node)
        else:
            new_node = nuke.createNode('Transform')
            if new_node:
                transform_nodes.append(new_node)
        unselect()
    select(transform_nodes)


def read_from_write():
    # Create read nodes from selected write nodes
    nodes = [n for n in nuke.selectedNodes() if 'file' in n.knobs()]
    excluded = ['Read', ]
    for node in nodes:
        if node.Class() in excluded:
            continue
        pos = get_pos(node)
        filepath = node['file'].getValue()
        if '[' in filepath:
            # contains tcl expression. use evaluate instead.
            filepath_eval = node['file'].evaluate()
            
        dirname = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        if '#' in filename:
            is_sequence = True
            filename_base = filename.split('#')[0]
        elif r'%' in filename:
            is_sequence = True
            filename_base = filename.split(r'%')[0]
        else:
            is_sequence = False
        if is_sequence:
            sequences = nuke.getFileNameList(dirname)
            for seq in sequences:
                if seq.startswith(filename_base):
                    filepath = os.path.join(dirname, seq)
                    break
        read = nuke.createNode('Read', 'file {{{0}}}'.format(filepath), inpanel=False)
        set_pos(read, pos[0], pos[1] + grid[1]*4)
        # match colorspace
        colorspace = node['colorspace'].value()
        if '(' in colorspace and ')' in colorspace:
            # parse out role
            colorspace = colorspace.split('(')[1].split(')')[0]
        read['colorspace'].setValue(colorspace)
        read['raw'].setValue(node['raw'].getValue())




# Enhanced swap functionality.
def swap_knob(knob):
    knob.setValue(0) if knob.getValue() == 1 else knob.setValue(1)

def swap_node(nodes=None):
    if not nodes:
        nodes = nuke.selectedNodes()
    for node in nodes:
        if node.inputs() > 1:
            nukescripts.swapAB(node)
        if node.Class() == 'OCIOColorSpace':
            in_colorspace = node['in_colorspace'].value()
            out_colorspace = node['out_colorspace'].value()
            node['out_colorspace'].setValue(in_colorspace)
            node['in_colorspace'].setValue(out_colorspace)
        if node.Class() == 'Colorspace':
            colorspace_in = node['colorspace_in'].value()
            colorspace_out = node['colorspace_out'].value()
            node['colorspace_out'].setValue(colorspace_in)
            node['colorspace_in'].setValue(colorspace_out)
        if 'direction' in node.knobs():
            swap_knob(node['direction'])
        if 'invert' in node.knobs():
            swap_knob(node['invert'])
        if 'invert_matrix' in node.knobs():
            swap_knob(node['invert_matrix'])
        if 'reverse' in node.knobs():
            swap_knob(node['reverse'])
        if 'operation' in node.knobs():
            opknob = node['operation']
            vals = list(opknob.values())
            if vals:
                if 'log' in vals[0]:
                    swap_knob(node['operation'])
        if 'Roto' in node.Class():
            if 'replace' in node.knobs():
                swap_knob(node['replace'])


def swap_view():
    views = nuke.views()
    if len(views) == 2:
        nuke.activeViewer().setView(views[1]) if nuke.activeViewer().view() == views[0] else nuke.activeViewer().setView(views[0])
