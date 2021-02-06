from __future__ import division
from builtins import zip
from builtins import str
from builtins import range
import nuke


def delete_pt():
    max_pts = int(nuke.thisNode().knob('Max PTS').value()) - 1

    if max_pts < 2:
        nuke.message('Minimum 2 points')
        return

    pt_num = int(nuke.thisKnob().name()[6:])
    node = nuke.thisNode()

    for pt in range(pt_num, max_pts):
        knob_name = 'pt' + str(pt)
        next_knob = 'pt' + str(pt + 1)
        node[knob_name].fromScript(node[next_knob].toScript())

    node.knob('pt' + str(max_pts)).clearAnimated()
    node.knob('pt' + str(max_pts)).setValue([0, 0])

    for name in ('pt', 'delete', 'insert'):
        node.knobs()[name + str(max_pts)].setVisible(False)

    node.knob('Max PTS').setValue(max_pts)


def insert_pt():
    max_pts = int(nuke.thisNode().knob('Max PTS').value())
    MAX_POINTS = int(nuke.thisNode().knob('Max Limit').value())

    if max_pts >= MAX_POINTS:
        nuke.message('Maximum %i points' % (MAX_POINTS))
        return

    pt_num = int(nuke.thisKnob().name()[6:])
    node = nuke.thisNode()

    # Shuffle values upwards
    for pt in range(max_pts, pt_num, -1):
        knob_name = 'pt' + str(pt)
        prev_knob = 'pt' + str(pt - 1)
        node[knob_name].fromScript(node[prev_knob].toScript())

    # Set new position to midpoint of adjacent points
    if pt_num > 1:
        ptA = node.knob('pt' + str(pt_num - 1)).value()
    else:
        ptA = node.knob('Start').value()
    ptB = node.knob('pt' + str(pt_num + 1)).value()
    midpoint = [sum(x) / 2 for x in zip(ptA, ptB)]

    node.knob('pt' + str(pt_num)).clearAnimated()
    node.knob('pt' + str(pt_num)).setValue(midpoint)

    # Reveal next row
    for name in ('pt', 'delete', 'insert'):
        node.knobs()[name + str(max_pts)].setVisible(True)

    node.knob('Max PTS').setValue(max_pts + 1)


def add_pt():
    max_pts = int(nuke.thisNode().knob('Max PTS').value())
    MAX_POINTS = int(nuke.thisNode().knob('Max Limit').value())

    if max_pts >= MAX_POINTS:
        nuke.message('Maximum %i points' % (MAX_POINTS))
        return

    node = nuke.thisNode()

    for name in ('pt', 'delete', 'insert'):
        node.knobs()[name + str(max_pts)].setVisible(True)

    node.knob('Max PTS').setValue(max_pts + 1)


def initialiseNode(node, max_num=4):

    node.knob(node.name()).setLabel('Appearance')

    knob_names = [x for x in list(node.knobs().keys()) if x.startswith('pt')]
    knob_names.sort(key=lambda x: int(x[2:]))

    # Add new Tab for points
    start_knob = node.knobs()['Start']
    node.removeKnob(start_knob)
    node.addKnob(nuke.Tab_Knob('Points'))
    text = "Insert adds a point between its adjacent and previous point\nDelete removes the adjacent point\nAdd adds a point at the end"
    node.addKnob(nuke.Text_Knob('info', '', text))
    node.addKnob(nuke.Text_Knob('', ''))
    node.addKnob(start_knob)

    # Remove and store all pt knobs
    knobs = []
    for name in knob_names:
        knob = node.knobs()[name]
        knobs.append(knob)
        node.removeKnob(knob)

    # Add each back along with their delete and insert buttons
    for knob in knobs:
        num = knob.name()[2:]

        delete = nuke.PyScript_Knob('delete' + num, 'Delete', "Lines_Callbacks.delete_pt()")
        insert = nuke.PyScript_Knob('insert' + num, 'Insert', "Lines_Callbacks.insert_pt()")

        # Hide knobs greater than the max value
        if int(num) >= max_num:
            knob.setVisible(False)
            delete.setVisible(False)
            insert.setVisible(False)

        node.addKnob(knob)
        node.addKnob(delete)
        node.addKnob(insert)

    # Add the Add knob
    add_knob = nuke.PyScript_Knob('add_pt', 'Add', "Lines_Callbacks.add_pt()")
    add_knob.setFlag(nuke.STARTLINE)
    node.addKnob(add_knob)

    node.knob('Max PTS').setValue(max_num)
    node.knobs()['Max PTS'].setVisible(False)
    node.knobs()['Max Limit'].setVisible(False)
