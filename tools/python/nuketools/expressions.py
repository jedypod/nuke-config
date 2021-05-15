from __future__ import print_function
from __future__ import absolute_import
import nuke
from six.moves import range

# Bake all knobs with expressions to keyframes

nuke.menu('Nuke').addCommand('Edit/Node/Bake Expressions', 'expressions.bake(nuke.selectedNodes(), nuke.root().firstFrame(), nuke.root().lastFrame())', 'ctrl+alt+meta+shift+b')

def bake(nodes, start, end):
    for node in nodes:
        for knob in list(node.knobs().values()):
            if isinstance(knob, nuke.Link_Knob):
                knob = knob.getLinkedKnob()
            if knob.hasExpression():
                if knob.singleValue():
                    array_size = 1
                else:
                    array_size = knob.arraySize()
                for index in range(array_size):
                    if knob.hasExpression(index):
                        anim = knob.animation(index)
                        anim_keys = []
                        for frame in range(start, end + 1):
                            anim_keys.append(nuke.AnimationKey(frame, anim.evaluate(frame)))
                        anim.addKey(anim_keys)
                        knob.setExpression("curve", index)
                        if anim.constant():
                            knob.clearAnimated(index)
