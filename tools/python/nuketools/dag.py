import nuke
import nukescripts
import operator, math, os


# Utilities for enhancing efficiency when interacting with Nuke's Directed Acyclic Graph


# Register keyboard shortcuts and menu entries
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Right', 'dag.move(4, 0)', 'alt+meta+Right')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Left', 'dag.move(-4, 0)', 'alt+meta+Left')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Up', 'dag.move(0, -4)', 'alt+meta+Up')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Down', 'dag.move(0, 4)', 'alt+meta+Down')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Right Big', 'dag.move(1, 0)', 'alt+meta+shift+Right')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Left Big', 'dag.move(-1, 0)', 'alt+meta+shift+Left')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Up Big', 'dag.move(0, -1)', 'alt+meta+shift+Up')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Move/Move Down Big', 'dag.move(0, 1)', 'alt+meta+shift+Down')

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Up Vertical', 'dag.scale(1, 2)', 'meta+shift++', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Down Vertical', 'dag.scale(1, 0.5)', 'meta+shift+_', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Up Horizontal', 'dag.scale(0, 2)', 'meta+=', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Scale/Scale Down Horizontal', 'dag.scale(0, 0.5)', 'meta+-', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Mirror Horizontally', 'dag.scale(0, -1, pivot="min")', 'meta+m')
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Mirror Vertically', 'dag.scale(0, -1, pivot="max")', 'meta+shift+m')

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Left', 'dag.align("left")', 'ctrl+shift+left', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Right', 'dag.align("right")', 'ctrl+shift+right', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Up', 'dag.align("up")', 'ctrl+shift+up', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Align/Down', 'dag.align("down")', 'ctrl+shift+down', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Snap to Grid', 'dag.snap_to_grid()', 'alt+s', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Connect to Closest', 'dag.connect_to_closest()', 'meta+shift+y', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Paste To Selected', 'dag.paste_to_selected()', 'alt+v', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar Class', 'nuke.selectSimilar(nuke.MATCH_CLASS)', 'alt+meta+shift+s', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar Color', 'nuke.selectSimilar(nuke.MATCH_COLOR)', 'alt+meta+shift+c', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar Y Position', 'dag.select_similar_position(axis=1)', 'alt+meta+v', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Similar/Select Similar X Position', 'dag.select_similar_position(axis=0)', 'alt+meta+shift+v', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Upstream', 'dag.select_upstream(nuke.selectedNodes())', 'alt+meta+shift+u', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Invert Selection', 'nuke.invertSelection()', 'alt+meta+shift+i', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Connected Nodes', 'dag.select_connected(nuke.selectedNodes())', 'alt+meta+shift+o', shortcutContext=2)
nuke.menu('Nuke').addCommand('Edit/Select Downstream', 'dag.select_downstream(nuke.selectedNodes())', 'alt+meta+shift+p', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Properties Panel Open', 'dag.open_panels()', 'a', shortcutContext=1)
nuke.menu('Nuke').addCommand('Edit/Node/DAG/Properties Panel Close', 'dag.close_panels()', 'alt+a', shortcutContext=1)

nuke.menu('Nuke').addCommand('Edit/Node/DAG/Sort By File Knob', 'dag.auto_place()', 'l', shortcutContext=2)

nuke.menu('Nuke').addCommand('Edit/Node/Declone', 'dag.declone_nodes(nuke.selectedNodes())', 'alt+shift+k', shortcutContext=2)
nuke.menu('Nuke').addCommand('File/Export Selected with Root Settings', 'dag.export_selected_nodes()', 'ctrl+shift+e', index=7)
nuke.menu('Nuke').addCommand('File/Import Script', 'nukescripts.import_script()', 'ctrl+shift+i', index=8)


nuke.menu('Nuke').addCommand('Edit/Node/Swap A - B', 'dag.swap_node()', 'shift+x')
nuke.menu('Viewer').addCommand("Swap View", "dag.swap_view()", "shift+q")

nuke.menu('Nodes').addCommand( 'Transform/Transform', 'dag.create_transform()', 't')


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

# Hlink Nodes
nuke.menu('Nuke').addCommand('Edit/HLink Cut', 'dag.hlink_cut()', 'ctrl+x')
nuke.menu('Nuke').addCommand('Edit/HLink Copy', 'dag.hlink_copy()', 'ctrl+c')
nuke.menu('Nuke').addCommand('Edit/HLink Paste', 'dag.hlink_paste()', 'ctrl+v')
nuke.menu('Nuke').addCommand('Edit/HLink Create', 'dag.hlink_create()', 'alt+shift+p')
nuke.menu('Nuke').addCommand('Edit/Paste', 'nuke.nodePaste("%clipboard%")', 'ctrl+shift+v', index=6)








# Get the grid size from the preferences. Used as the default unit of movement.
grid = (int(nuke.toNode('preferences').knob('GridWidth').value()), int(nuke.toNode('preferences').knob('GridHeight').value()))


def unselect(nodes=None):
    # Unselect nodes
    if not nodes:
        nodes = nuke.allNodes(recurseGroups=True)
    _ = [n.setSelected(False) for n in nodes]


def select(nodes):
    # Select specified nodes
    _ = [n.setSelected(True) for n in nodes]


def get_parent(node):
    # return node's parent node, return nuke.root() if on the top level
    return nuke.toNode('.'.join(node.fullName().split('.')[:-1])) or nuke.root()


def get_topnode(node):
    # return the topnode of node
    pass


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
    # Always hide control panels on node creation
    nuke.thisNode().showControlPanel()
    nuke.thisNode().hideControlPanel()
nuke.addOnUserCreate(hide_panel)


def open_panels(nodes=None):
    # Open properties panels
    if not nodes:
        nodes = nuke.selectedNodes()
    ignored = ['Viewer']
    if len(nodes) > 10:
        if not nuke.ask('Continuing will open {0} properties panels. \nAre you sure you want to continue?'.format(len(nodes))):
            return
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


def close_panels(nodes=None):
    # Close properties panels
    if not nodes:
        nodes = nuke.selectedNodes()
    if not nodes:
        # Close all panels if no nodes selected
        nodes = nuke.allNodes(recurseGroups=True)
    for node in nodes:
        node.hideControlPanel()


def select_similar_position(axis=1):
    node = nuke.selectedNode()
    if not node:
        return
    threshold = 1
    unselect()
    if axis:
        same_pos_nodes = {n:n.xpos() for n in nuke.allNodes() if abs(n.ypos()- node.ypos()) < threshold}
    else:
        same_pos_nodes = {n:n.ypos() for n in nuke.allNodes() if abs(n.xpos()- node.xpos()) < threshold}
    sorted_nodes = sorted(same_pos_nodes.items(), key=operator.itemgetter(1))
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
        sorted_filenodes = sorted(filenodes.items(), key=operator.itemgetter(1))
        filenodes_pos = {n: [n.xpos(), n.ypos()] for n in nodes if 'file' in n.knobs()}
        ypos_sort = sorted(filenodes_pos.items(), key=lambda (k, v): v[1])
        xpos_sort = sorted(filenodes_pos.items(), key=lambda (k, v): v[0])
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


def move(xvel, yvel):
    # Move selected nodes by specified number of grid lengths in x and y
    yvel *= 3
    nodes = nuke.selectedNodes()
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


def connect_to_closest():
    # Connect next available input of all selected nodes to the closest node
    for node in nuke.selectedNodes():
        closest = get_closest_node(node)
        node.connectInput(0, closest)


def paste_to_selected():
    nodes = nuke.selectedNodes()
    unselect()
    pasted = list()
    for node in nodes:
        node.setSelected(True)
        pasted.append(nuke.nodePaste('%clipboard'))
        unselect()
    for node in pasted:
        node.setSelected(True)


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
        print 'Error: invalid direction specified: {0}'.format(direction)
        return

    positions = {n: get_pos(n) for n in nodes}
    sorted_positions = sorted(positions.items(), key=lambda (k, v): v[align])
    if direction in ['down', 'right']:
        sorted_positions.reverse()
    target = sorted_positions[0]
    target_pos = target[1]

    offset = 0

    other_axis = abs(1 - align)

    sorted_other_axis = sorted(positions.items(), key=lambda (k, v): v[other_axis])

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
    sort = sorted(positions.items(), key=lambda (k, v): v[axis])

    minpos = sort[0][1][axis]
    maxpos = sort[-1][1][axis]

    if pivot == 'max':
        pivot_pos = maxpos
    elif pivot == 'min':
        pivot_pos = minpos
    elif pivot == 'center':
        pivot_pos = (minpos - maxpos)/2 + minpos

    nuke.Undo().begin()
    for node, pos in positions.iteritems():
        if axis:
            set_pos(node, pos[0], (pos[1] - pivot_pos) * scale + pivot_pos)
            if node.Class() == 'BackdropNode':
                node['bdheight'].setValue(
                    ((pos[1] + node['bdheight'].getValue()) - pivot_pos)
                     * scale + pivot_pos - node.ypos())

        else:
            set_pos(node, (pos[0] - pivot_pos) * scale + pivot_pos, pos[1])
            if node.Class() == 'BackdropNode':
                node['bdwidth'].setValue(
                    ((pos[0] + node['bdwidth'].getValue()) - pivot_pos)
                     * scale + pivot_pos - node.xpos())
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
    _ = [n.setSelected(True) for n in connected(nodes, upstream=True, downstream=False)]

def select_downstream(nodes):
    # Select all downstream dependencies of node
    _ = [n.setSelected(True) for n in connected(nodes, upstream=False, downstream=True)]

def select_connected(nodes):
    # Select all nodes connected to node
    _ = [n.setSelected(True) for n in connected(nodes, upstream=True, downstream=True)]





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





def create_transform():
    # Create a Transform or TransformGeo node depending on node type
    nodes = nuke.selectedNodes()
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


# Enhanced swap functionality.
def swap_node():
    nodes = nuke.selectedNodes()
    for node in nodes:
        if node.inputs() > 1:
            nukescripts.swapAB(node)
        if node.Class() == 'OCIOColorSpace':
            in_colorspace = node['in_colorspace'].value()
            out_colorspace = node['out_colorspace'].value()
            node['out_colorspace'].setValue(in_colorspace)
            node['in_colorspace'].setValue(out_colorspace)
        elif 'direction' in node.knobs():
            direction = node['direction']
            if direction.getValue() == 1:
                direction.setValue(0)
            else:
                direction.setValue(1)
        elif 'invert' in node.knobs():
            invert = node['invert']
            if invert.getValue() == 1:
                invert.setValue(0)
            else:
                invert.setValue(1)
        elif node.Class() == 'Colorspace':
            colorspace_in = node['colorspace_in'].value()
            colorspace_out = node['colorspace_out'].value()
            node['colorspace_out'].setValue(colorspace_in)
            node['colorspace_in'].setValue(colorspace_out)

def swap_view():
    views = nuke.views()
    if len(views) == 2:
        nuke.activeViewer().setView(views[1]) if nuke.activeViewer().view() == views[0] else nuke.activeViewer().setView(views[0])