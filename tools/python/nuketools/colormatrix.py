from __future__ import print_function
from builtins import range
import nuke

nuke.toolbar('Nodes').addCommand('Color/ColorMatrix Combine', 'colormatrix.process(nuke.selectedNodes())')

float3x3 = nuke.math.Matrix3

def matrix_from_node(node):
    # return 3x3 matrix object from node
    if not 'matrix' in node.knobs():
        print('Error: node {0} does not contain a matrix knob.'.format(
            node.fullName()))
        return None
    mtx_list = node['matrix'].getValue()
    M = float3x3()
    for i in range(9):
        M[i] = mtx_list[i]
    if node['invert'].getValue():
        M = M.inverse()
    return M

def process(nodes):
    # Process all nodes. Combine all colormatrix nodes in order that they are connected. Bake invert knobs to false.
    if not nodes:
        return
    _ = [n.setSelected(False) for n in nuke.allNodes(recurseGroups=True)]
    matrices = [matrix_from_node(n) for n in nodes if 'matrix' in n.knobs()]
    node = nuke.createNode('ColorMatrix')
    node.setXYpos(nodes[0].xpos()-140, nodes[0].ypos())
    if len(matrices) > 1:
        M = float3x3()
        num = len(matrices)
        for i in range(num-1):
            A = matrices[i]
            if i == 0:
                M = A
            B = matrices[i+1]
            M = M * B
        node['matrix'].setValue(M)
    elif len(matrices) == 1:
        # Set the matrix
        node['matrix'].setValue(matrices[0])
        node['invert'].setValue(0)