from __future__ import (print_function,
                        absolute_import,
                        division,
                        unicode_literals,
                        with_statement,
                        )
from builtins import range
import nuke, os, re
import nukescripts


nuke.menu('Nuke').addCommand('Edit/Node/Bake Gizmos to Groups', 'bake_gizmos.bake_selected_gizmos()', 'ctrl+alt+shift+meta+g')


def get_all_nodes(topLevel):
    '''
    recursively return all nodes starting at topLevel. Default topLevel is nuke.root()
    '''
    allNodes = nuke.allNodes( group=topLevel )
    for n in allNodes:
        allNodes = allNodes+get_all_nodes( n )
    return allNodes

def get_outputs(gizmo):
    '''
    Return a dictionary of the nodes and pipes that are connected to node
    '''
    depDict = {}
    
    # There appears to be a bug with the dependent() function where sometimes the first time you run it after a nuke script is opened, it returns nothing.
    # To work around this we will call dependent twice, just in case it's the first gizmo we're baking in the script.
    tmp = gizmo.dependent( nuke.INPUTS | nuke.HIDDEN_INPUTS )
    dependents = gizmo.dependent( nuke.INPUTS | nuke.HIDDEN_INPUTS )
    del(tmp)

    # Iterate through each node that is connected to the gizmo
    for dep in dependents:
        # Add each dependency as a dictionary key, with a blank list
        # The list will contain what input of the dep is connected to our gizmo
        depDict[dep] = []

        # Loop through each input of dep, check if that input is connected to gizmo
        # If so, add the input number to the list that is the value of the dep key in the dict
        for i in range( dep.inputs() ):
            if dep.input( i ) == gizmo:
                depDict[ dep ].append( i )
    return depDict

def is_gizmo(node):
    '''
    return True if node is gizmo
    '''
    return 'gizmo_file' in node.knobs()

def gizmo_is_default(gizmo):
    '''Check if gizmo is in default install path'''
    installPath = os.path.dirname(nuke.EXE_PATH)
    gizmoPath = gizmo.filename()
    if gizmoPath:
        installPathSet = set(installPath.split('/'))
        gizmoPathSet = set(gizmoPath.split('/'))
        gizmoPathSet.issubset(installPathSet)
        gizmo_is_default = os.path.commonprefix([installPath, gizmoPath]) == installPath
    else:
        gizmo_is_default = False
    return gizmo_is_default

def get_parent( n ):
    '''
    return n's parent node, return nuke.root()n if on the top level
    '''
    return nuke.toNode( '.'.join( n.fullName().split('.')[:-1] ) ) or nuke.root()


def bake_gizmo( gizmo ):
    '''
    copy gizmo to group and replace it in the tree, so all inputs and outputs use the new group.
    returns the new group node
    '''
    parent = get_parent( gizmo )
    gizmo_outputs = get_outputs(gizmo)
    gizmo_inputs = gizmo.inputs()

    print("INPUTS:", gizmo_inputs) #[inputnodes.name() for inputnodes in gizmo_inputs]
    print("OUTPUTS:", gizmo_outputs) #[output_nodes.name() for output_nodes in gizmo_outputs]

    # This old method can't detect failures
    #groupName = nuke.tcl( 'global no_gizmo; set no_gizmo 1; in %s {%s -New} ; return [value [stack 0].name]' % ( parent.fullName(), gizmo.Class() ) )
    for n in get_all_nodes(nuke.root()):
        n.setSelected(False)
    try:
        nuke.tcl('copy_gizmo_to_group {0}'.format(gizmo.fullName()))
        #group = nuke.toNode( '.'.join( (parent.fullName(), groupName) ) )
        ## We will use the selected node to get the created group
        group = nuke.selectedNode()

        if gizmo_outputs:
            #RECONNECT OUTPUTS IF THERE ARE ANY
            for node, pipes in gizmo_outputs.items():
                for i in pipes:
                    node.setInput( i, group )

        #RECONNECT INPUTS
        for i in range( gizmo.inputs() ):
            group.setInput( i, gizmo.input( i ) )
        group.setSelected( False )

    except RuntimeError:
        # Occurs if the gizmo was sourced: "RuntimeError: This gizmo was created with a "load" or "source" command. Copy to group does not work for it."
        print("This gizmo was created with a 'load' or 'source' command. Manually re-creating it...")
        with parent:
            # gizmo.Class() fails because the gizmo class is defined as "Gizmo" - super hacky but we'll try to use the node's name
            gizmo_guess_class = re.split('[0-9]*$', gizmo.name())[0]
            tmp_gizmo = nuke.createNode(gizmo_guess_class, inpanel=False)
            nuke.tcl('copy_gizmo_to_group {0}'.format(tmp_gizmo.fullName()))
            
        # fix bug where the copy_gizmo_to_group puts node outside of the parent: cut node outside group, paste node inside group
        nuke.nodeCopy(nukescripts.cut_paste_file()); nukescripts.node_delete(popupOnError=True)
        with parent:
            nuke.nodePaste(nukescripts.cut_paste_file())

            group = nuke.selectedNode()
            nuke.delete(tmp_gizmo)
            group.setSelected( False )

    group.hideControlPanel()
    

    if gizmo_outputs:
        #RECONNECT OUTPUTS IF THERE ARE ANY
        for node, pipes in gizmo_outputs.items():
            for i in pipes:
                node.setInput( i, group )

    #RECONNECT INPUTS
    for i in range( gizmo_inputs ):
        group.setInput( i, gizmo.input( i ) )

    group.setXYpos( gizmo.xpos(), gizmo.ypos() )
    # COPY VALUES
    group.readKnobs( gizmo.writeKnobs(nuke.TO_SCRIPT) )
    gizmoName = gizmo.name()
    nuke.delete( gizmo )
    group.setName(gizmoName)
    return group
    

def bake_gizmos(topLevel=nuke.root(), exclude_default=True):
    
    # Store the selected Nodes, we store names because the bake can mess up the python binding
    names = [n.name() for n in nuke.selectedNodes()]
    
    for n in get_all_nodes(topLevel):
        n.setSelected(False)
        
    for n in get_all_nodes(topLevel):
        try:
            if is_gizmo(n):
                if not gizmo_is_default(n):
                    # ALWAYS BAKE CUSTOM GIZMOS
                    print("Baking:", n.fullName())
                    bake_gizmo(n)
                elif not exclude_default:
                    # BAKE NON-DEFAULT GIZMOS IF REQUESTED
                    bake_gizmo(n)
                
        except ValueError:
            pass
    
    # Reselect the selected Nodes
    for node in nuke.allNodes():
        node.setSelected(False)
        
    for name in names:
        node = nuke.toNode(name)
        if node:
            node.setSelected(True)


def bake_selected_gizmos(topLevel=nuke.root(), exclude_default=True):
    nodes = [n for n in nuke.selectedNodes() if is_gizmo(n)]
    for node in nodes:
        if not gizmo_is_default(node):
            # ALWAYS BAKE CUSTOM GIZMOS
            print("Baking:", node.fullName())
            bake_gizmo(node)
        elif not exclude_default:
            # BAKE NON-DEFAULT GIZMOS IF REQUESTED
            bake_gizmo(node)
