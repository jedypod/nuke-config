from __future__ import print_function
import nuke
import nukescripts
import nuke.rotopaint as rp
import _curvelib as cl

nuke.menu('Nuke').addCommand('Edit/Node/Create Linked Roto', 'linker.link("roto")', 'alt+o')
nuke.menu('Nuke').addCommand('Edit/Node/Create Linked Node', 'linker.link()', 'alt+l')


def link_transform(target_node):
    """
    Utility function for link_transform: creates linked transform node
    """
    grid_x = int(nuke.toNode('preferences').knob('GridWidth').value())
    grid_y = int(nuke.toNode('preferences').knob('GridHeight').value())

    target_name = target_node.name()
    nclass = target_node.Class()
    if "Tracker" not in nclass and "Transform" not in nclass:
        print("Must select Tracker or Transform node!")
        return

    target_node.setSelected(False)
    # Create linked Transform Node
    trans = nuke.createNode('Transform')
    trans.setName('TransformLink')
    trans.setSelected(True)
    trans.knob('help').setValue("<b>TransformLink</b>\n\nA Transform node with options for linking to a Tracker or a Transform node. \n\nAllows you to set a seperate identity transform frame from the linked Tracker. Select the link target and click 'Set Target', or set the link target by name. You can also bake the expression link into keyframes if you want it independant from the target node. \n\nThe transform Matchmoves or Stabilizes depending on what the parent tracker node is set to, but you can invert this by enabling the 'invert' checkbox.")
    trans.knob('label').setValue(target_node.name())
    trans.setXYpos(target_node.xpos()-grid_x*0, target_node.ypos()+grid_y*2)
    trans.addKnob(nuke.Tab_Knob('TrackLink'))
    trans.addKnob(nuke.Int_Knob('reference_frame', 'reference frame'))


    if 'Tracker' in nclass:
        trans.knob('reference_frame').setValue( int(target_node.knob('reference_frame').value()) )
    else:
        trans.knob('reference_frame').setValue(nuke.frame())

    trans.addKnob(nuke.PyScript_Knob('identity_to_curframe', 'Set to Current Frame'))
    trans.knob('identity_to_curframe').setTooltip("Set identity frame to current frame.")
    trans.knob('identity_to_curframe').setCommand("nuke.thisNode().knob('reference_frame').setValue(nuke.frame())")
    trans.knob('identity_to_curframe').setFlag(nuke.STARTLINE)
    trans.addKnob(nuke.PyScript_Knob('bake_link', 'Bake Expression Links'))

    trans.knob('bake_link').setTooltip('Bake expression links to keyframes')
    trans.knob('bake_link').setCommand('''import tools.expressions
node = nuke.thisNode()
try:
    target_node = nuke.toNode(node['link_target'].value())
    first_frame = int(target_node['translate'].animation(0).keys()[0].x)
    last_frame = int(target_node['translate'].animation(0).keys()[-1].x)
except:
    first_frame = nuke.root()['first_frame']
    last_frame = nuke.root()['last_framed']
tools.expressions.bake([node], first_frame, last_frame)''')

    # add target node as a knob so we can use it later
    trans.addKnob(nuke.Text_Knob("link_target"))
    target_node_knob = trans['link_target']
    target_node_knob.setValue(target_node.name())
    target_node_knob.setVisible(False)

    # # Link knobs
    trans.knob('translate').setExpression('parent.{0}.translate - parent.{0}.translate(reference_frame)'.format(target_name))
    trans.knob('rotate').setExpression('parent.{0}.rotate - parent.{0}.rotate(reference_frame)'.format(target_name))
    trans.knob('scale').setExpression('parent.{0}.scale / parent.{0}.scale(reference_frame)'.format(target_name))
    trans.knob('skewX').setExpression('parent.{0}.skewX - parent.{0}.skewX(reference_frame)'.format(target_name))
    trans.knob('skewY').setExpression('parent.{0}.skewY - parent.{0}.skewY(reference_frame)'.format(target_name))
    trans.knob('center').setExpression('parent.{0}.center+parent.{0}.translate(reference_frame)'.format(target_name))



def link_roto(tracker_node, roto_node=False):
    '''
    Utility function: Creates a layer in roto_node linked to tracker_node
    if roto_node is False, creates a roto node next to tracker node to link to
    '''
    grid_x = int(nuke.toNode('preferences').knob('GridWidth').value())
    grid_y = int(nuke.toNode('preferences').knob('GridHeight').value())

    tracker_name = tracker_node.name()
    tracker_node.setSelected(False)

    # If Roto node not selected, create one.
    if not roto_node:
        roto_node = nuke.createNode('Roto')
        roto_node.setXYpos(tracker_node.xpos()-grid_x*0, tracker_node.ypos()+grid_y*2)
        roto_node.setSelected(True)

    # Create linked layer in Roto Node
    curves_knob = roto_node["curves"]
    stab_layer = rp.Layer(curves_knob)
    stab_layer.name = "stab_"+tracker_name

    trans_curve_x = cl.AnimCurve()
    trans_curve_y = cl.AnimCurve()

    trans_curve_x.expressionString = "parent.{0}.translate.x".format(tracker_name)
    trans_curve_y.expressionString = "parent.{0}.translate.y".format(tracker_name)
    trans_curve_x.useExpression = True
    trans_curve_y.useExpression = True

    rot_curve = cl.AnimCurve()
    rot_curve.expressionString = "parent.{0}.rotate".format(tracker_name)
    rot_curve.useExpression = True

    scale_curve = cl.AnimCurve()
    scale_curve.expressionString = "parent.{0}.scale".format(tracker_name)
    scale_curve.useExpression = True

    center_curve_x = cl.AnimCurve()
    center_curve_y = cl.AnimCurve()
    center_curve_x.expressionString = "parent.{0}.center.x".format(tracker_name)
    center_curve_y.expressionString = "parent.{0}.center.y".format(tracker_name)
    center_curve_x.useExpression = True
    center_curve_y.useExpression = True

    # Define variable for accessing the getTransform()
    transform_attr = stab_layer.getTransform()
    # Set the Animation Curve for the Translation attribute to the value of the previously defined curve, for both x and y
    transform_attr.setTranslationAnimCurve(0, trans_curve_x)
    transform_attr.setTranslationAnimCurve(1, trans_curve_y)
    # Index value of setRotationAnimCurve is 2 even though there is only 1 parameter...
    # http://www.mail-archive.com/nuke-python@support.thefoundry.co.uk/msg02295.html
    transform_attr.setRotationAnimCurve(2, rot_curve)
    transform_attr.setScaleAnimCurve(0, scale_curve)
    transform_attr.setScaleAnimCurve(1, scale_curve)
    transform_attr.setPivotPointAnimCurve(0, center_curve_x)
    transform_attr.setPivotPointAnimCurve(1, center_curve_y)
    curves_knob.rootLayer.append(stab_layer)



def link_camera(src_cam, proj_frame, expr_link, clone, index):
    """
        Create a linked camera to src_cam -- this camera can be frozen on a projection frame
    """
    # Default grid size is 110x24. This enables moving by grid increments.
    # http://forums.thefoundry.co.uk/phpBB2/viewtopic.php?t=3739&sid=c40e65b1f575ba9166583faf807184ee
    # Offset by 1 grid in x for each additional iteration
    grid_x = int(nuke.toNode('preferences').knob('GridWidth').value())
    grid_y = int(nuke.toNode('preferences').knob('GridHeight').value())*index

    src_cam.setSelected(False)

    # Create Projection Camera
    proj_cam = nuke.createNode('Camera2')

    # Create Projection Frame knob
    frame_tab = nuke.Tab_Knob('Frame')
    proj_cam.addKnob(frame_tab)
    proj_frame_knob = nuke.Double_Knob('proj_frame')
    if clone:
        proj_frame_knob.setExpression('t')
    else:
        proj_frame_knob.setValue(proj_frame)

    proj_cam.addKnob(proj_frame_knob)

    ## Copy the knob values of the Source Camera
    for knob_name, knob in src_cam.knobs().items():
        # For Animated knobs, copy or link the values depending on if Expression Links are enabled.
        if knob.isAnimated():
            #print "setting animated knob", knob_name
            if expr_link == True:
                #print "setting expression for animated knobs"
                for index in range(src_cam.knob(knob_name).arraySize()):
                    if src_cam.knob(knob_name).isAnimated(index):
                        proj_cam[knob_name].copyAnimation(index, src_cam[knob_name].animation(index))
                proj_cam[knob_name].setExpression('parent.' + src_cam.name() + "." + knob_name + "(proj_frame)")
            # http://www.nukepedia.com/python/knob-animation-and-python-a-primer/
            else:
                for index in range(src_cam.knob(knob_name).arraySize()):
                    if src_cam.knob(knob_name).isAnimated(index):
                        proj_cam[knob_name].copyAnimation(index, src_cam[knob_name].animation(index))
                proj_cam[knob_name].setExpression('curve(proj_frame)')

        # For all non-animated knobs that are not set to default values, match value from src_cam
        elif hasattr(knob, "notDefault") and knob.notDefault():
            try:
                #print "changing ", knob_name
                proj_cam[knob_name].setValue(knob.value())
            except TypeError:
                pass

    # Set label, color, name, and position
    proj_cam.setXYpos(src_cam.xpos()-grid_x, src_cam.ypos()-grid_y*4)
    if clone:
        proj_cam.setName("{0}_CLONE_".format(src_cam.name()))
        proj_cam["gl_color"].setValue(0xff5f00ff)
        proj_cam["tile_color"].setValue(0xff5f00ff)
    else:
        proj_cam.setName("{0}_PROJ_".format(src_cam.name()))
        proj_cam["gl_color"].setValue(0xffff)
        proj_cam["tile_color"].setValue(0xffff)
        proj_cam["label"].setValue("FRAME [value proj_frame]")



def link(link_type=None):
    nodes = nuke.selectedNodes()
    track_nodes = [n for n in nodes if 'Tracker' in n.Class()]
    cam_nodes = [n for n in nodes if n.Class() in ['Camera', 'Camera2']]
    roto_nodes = [n for n in nodes if n.Class() in ['Roto', 'RotoPaint', 'SplineWarp3']]
    xform_nodes = [n for n in nodes if n.Class() == 'Transform']

    if link_type == 'roto':
        if len(track_nodes) == 0:
            print("Error: At least one Tracker node must be selected.")
            return
        if len(roto_nodes) > 1 and len(track_nodes) > 1:
            print("Error: if multiple roto nodes are selected, exactly 1 Tracker node must be selected.")
            return
        for track_node in track_nodes:
            if len(roto_nodes) is 0:
                link_roto(track_node)
            if len(roto_nodes) >= 1:
                for roto_node in roto_nodes:
                    link_roto(track_node, roto_node)

    if link_type == None:
        for track_node in track_nodes:
            link_transform(track_node)
        for xform_node in xform_nodes:
            link_transform(xform_node)
        for cam_node in cam_nodes:
            ## Set up camera linker panel
            p = nuke.Panel('Camera Linker: {0}'.format(cam_node.name()))
            p.setWidth(450)
            p.addSingleLineInput('Frame', str(nuke.frame()))
            p.addBooleanCheckBox("Clone", False)
            p.addBooleanCheckBox('Link', True)
            if p.show():
                clone = p.value('Clone')
                framestring = p.value('Frame')
                expr_link = p.value('Link')
            else:
                # Cancelled
                return
            ## Parse frame string
            if "," in framestring:
                framelist = list(map(int, framestring.split(',')))
                for i, frame in enumerate(framelist):
                    link_camera(cam_node, frame, expr_link, clone, i)
            else:
                try:
                    framestring = int(framestring)
                except:
                    print("Error converting frame to integer!")
                    return
                link_camera(cam_node, framestring, expr_link, clone, 0)