from __future__ import print_function
import nuke

nuke.menu('Nuke').addCommand('Edit/Node/Change Knob Values', 'edit_nodes.edit_knobs()', 'ctrl+e')
nuke.menu('Nuke').addCommand('Edit/Node/Paste Knob Value', 'edit_nodes.paste_knobs()', 'ctrl+alt+v')
nuke.menu('Nuke').addCommand('Edit/Node/Paste Selected Knob Values', 'edit_nodes.paste_knobs(checkboxes=True)', 'ctrl+alt+shift+v')

def intersection(a, b):
    # calculate intersection between list a and list b
    return list(set(a)&set(b))

def get_knobs(node):
    # Add suported knobs from node and return a list of knob names
    unsupported_classes = [
        'LookupCurves_Knob', 
        'PythonKnob', 
        'Tab_Knob', 
        'Obsolete_Knob', 
        'ChannelMask_Knob', 
        'Font_Knob', 
        'ColorChip_Knob',
        'Text_Knob',
        ]
    unsupported_names = [
        'xpos', 'ypos', 'selected', 'gl_color', 'rootNodeUpdated', 'onDestroy', 
        'onCreate', 'updateUI', 'indicators', 'knobChanged', 
        ]
    ignore_patterns = ['_panelDropped']
    knobs = list()
    default_knobs = list()
    for k in node.knobs():
        knob = node[k]
        if knob.Class() not in unsupported_classes and knob.name() not in unsupported_names:
            for pattern in ignore_patterns:
                if pattern not in k:
                    knobs.append(k)
    return knobs


def edit_knobs():
    # Display all knobs that are common between all selected nodes.
    # Allow user to set expression or value on one of the knobs
    nodes = nuke.selectedNodes()
    # Find intersection of all knobs between all selected nodes
    knobs = list()
    for i in range(len(nodes)):
        if i == 0:
            knobs = get_knobs(nodes[i])
        else:
            knobs = intersection(get_knobs(nodes[i-1]), get_knobs(nodes[i]))
        i += 1
    knobs.sort()
    default_knob_names = [
        'hide_input', 'note_font', 'note_font_size', 'icon', 'dope_sheet', 'invert_mask', 
        'enable_mix_luminance', 'process_mask', 'lifetimeStart', 'unpremult', 'autolabel', 
        'invert_unpremult', 'postage_stamp_frame', 'postage_stamp', 'disable', 'maskChannel', 
        'name', 'lifetimeEnd', 'fringe', 'inject', 'maskChannelInput', 'maskChannelMask', 'maskFromFlag'
        ]
    default_knobs = list()
    node_knobs = list()
    for knob in knobs:
        if knob in default_knob_names:
            default_knobs.append(knob)
        else:
            node_knobs.append(knob)
    default_knobs.sort()
    node_knobs.sort()
    knobs = node_knobs + default_knobs
    panel = nuke.Panel('Edit Knobs')
    panel.setWidth(250)
    panel.addEnumerationPulldown('knobs', ' '.join(knobs))
    panel.addBooleanCheckBox('expression', 0)
    panel.addSingleLineInput('0', '')
    panel.addSingleLineInput('1', '')
    panel.addSingleLineInput('2', '')
    panel.addSingleLineInput('3', '')
    if not panel.show():
        return
    k = panel.value('knobs')
    create_expression = panel.value('expression')
    values = list()
    for i in range(4):
        val = panel.value(str(i))
        if val == '':
            values.append(False)
        else:
            try:
                values.append(float(val))
            except ValueError:
                values.append(str(val))
    for node in nodes:
        knob = node[k]
        try:
            array_size = knob.arraySize()
        except AttributeError:
            array_size = 1
        if create_expression:
            for i in range(array_size):
                if values[i]:
                    if knob.hasExpression(i):
                        knob.clearAnimated(i)
                    knob.setExpression(str(values[i]), channel=i)
        else:
            if isinstance(knob, nuke.Boolean_Knob):
                if knob.hasExpression():
                    knob.clearAnimated()
                if not values[0]:
                    knob.setValue(False)
                else:
                    knob.setValue(True)
            elif isinstance(knob, nuke.File_Knob):
                knob.setValue(values[0])
            elif isinstance(knob, nuke.Enumeration_Knob):
                if create_expression:
                    knob.setExpression(str(values[0]))
                else:
                    knob.setValue(values[0])
            elif isinstance(knob, (nuke.XYZ_Knob, nuke.XY_Knob, nuke.WH_Knob, nuke.UV_Knob, nuke.Array_Knob)):
                if knob.singleValue():
                    if values[0] and not values[1] and not values[2] and not values[3]:
                        # if only values[0] exists, set all in array_size to first value
                        knob.setValue(values[0])
                for i in range(array_size):
                    if knob.hasExpression(i):
                        knob.clearAnimated(i)
                    if isinstance(values[i], float):
                        knob.setValue(values[i], i)
                    elif isinstance(values[i], str):
                        # Assume this was meant to be an expression
                        knob.setExpression(str(values[i]), channel=i)


def paste_knobs(checkboxes=False):
    # Override of the ctrl+alt+v shortcut which allows pasting of only specified knob values to selected nodes
    # Only a single source node is supported unlike the original
    # Based on nukescripts.misc.copy_knobs()
    # If not checkboxes, all knobs or a single knob can be chosen
    # If checkboxes, an arbitrary selection of knobs can be chosen
    grp = nuke.thisGroup()
    dst_nodes = grp.selectedNodes()
    copy_grp = nuke.nodes.Group(name='____tempcopyknobgroup__')
    with copy_grp:
        nuke.nodePaste('%clipboard%')
    src_nodes = copy_grp.nodes()
    if src_nodes:
        src_node = src_nodes[-1]
    excluded_knobs = ['name', 'xpos', 'ypos', 'selected']
    try:
        intersect_knobs = dict()
        for dst_node in dst_nodes:
            src_knobs = src_node.knobs()
            dst_knobs = dst_node.knobs()
            intersection = dict(
                [(item, src_knobs[item]) for item in list(src_knobs.keys())
                 if item not in excluded_knobs and item in dst_knobs]
                )
            intersect_knobs.update(intersection)
        knobs = list(intersect_knobs.keys())
        panel = nuke.Panel('Choose Knobs')
        panel.setWidth(250)
        if checkboxes:
            # Checkboxes for each knob
            for k in knobs:
                panel.addBooleanCheckBox(k, 0)
        else:
            panel.addEnumerationPulldown('knob', ' '.join(knobs))
            panel.addBooleanCheckBox('paste all', 0)
        if not panel.show():
            return
        chosen_knobs = list()
        if checkboxes:
            for k in knobs:
                if panel.value(k):
                    chosen_knobs.append(k)
        else:
            paste_all = panel.value('paste all')
            if paste_all:
                chosen_knobs = knobs
            else:
                chosen_knobs.append(panel.value('knob'))
        for dst_node in dst_nodes:
            dst_knobs = dst_node.knobs()
            for knob in chosen_knobs:
                print('pasting src {0} to dst {1}'.format(knob, dst_node.name()))
                src = src_knobs[knob]
                dst = dst_knobs[knob]
                dst.fromScript(src.toScript())
    except Exception as e:
        nuke.delete(copy_grp)
        raise e
    nuke.delete(copy_grp)