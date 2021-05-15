from __future__ import with_statement
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import re
import glob
import subprocess

import nuke
import nukescripts
from six.moves import map
from six.moves import range


nuke.menu('Nuke').addCommand('Render/Terminal Render', 'terminal_render.render(nuke.selectedNodes())', index=6)


# Find Platform Type
from sys import platform as __platform

if __platform == "linux" or __platform == "linux2":
    _platform = 'linux'
elif __platform == "darwin":
    _platform = 'osx'
elif __platform == "win32":
    _platform = 'win'



if nuke.GUI:
    # Dialog state for local render
    _dstate = nukescripts.DialogState()

    def terminal_render(write_nodes, frameranges, views, instances, threads, mem):
        if _platform == "win":
            nuke.message("Windows not supported.")
            return
        nuke.scriptSave()
        script_path = nuke.root().knob("name").value()

        write_node_names = ','.join([n.fullName() for n in write_nodes])
        for framerange in frameranges:

            first_frame = framerange.minFrame()
            last_frame = framerange.maxFrame()

            num_frames = last_frame + 1 - first_frame
            chunk_size = int(num_frames / instances)

            for i in range(0, instances):
                render_start = first_frame + i * chunk_size
                render_end = first_frame + ((i+1) * chunk_size)
                if i > 0:
                    render_start += 1

                nk_cmd = '{0} -X {1} -c {2} -f -m {3} --view {4} -F {5}-{6} {7}'.format(
                    nuke.EXE_PATH, write_node_names, mem, threads, ','.join(map(str, views)),
                    str(render_start), str(render_end), script_path)

                print(nk_cmd)

                if _platform == "osx":
                    cmd = '''osascript 2>/dev/null <<EOF
                            tell application "Terminal"
                              if not (exists window 1) then reopen
                              activate
                              do script "{0}"
                            end tell
                            EOF'''.format(nk_cmd)
                elif _platform == "linux":
                    # cmd = 'xterm -e "bash {0}"'.format(nk_cmd)
                    # cmd = 'gnome-terminal -e "bash -c \\"{0}; exec bash\\""'.format(nk_cmd)
                    cmd = 'gnome-terminal -e "bash -c \\"{0}\\""'.format(nk_cmd)
                subprocess.Popen(cmd, shell=True)


    # Expanded from nukescripts.renderdialog
    class RenderDialog(nukescripts.ExecuteDialog):
        def _titleString(self):
            return "Render"

        def _idString(self):
            return "uk.co.thefoundry.RenderDialog"

        def __init__(self, dialogState, groupContext, nodeSelection = [], exceptOnError = True):
            nukescripts.ExecuteDialog.__init__(self, dialogState, groupContext, nodeSelection, exceptOnError)

        def _addPostKnobs(self):
            # Background render stuff
            self._bgRender = nuke.Boolean_Knob("bg_render", "Render in background")
            self._state.setKnob(self._bgRender, False)
            self._bgRender.setFlag(nuke.STARTLINE)
            self.addKnob(self._bgRender)

            # Terminal Render
            self._termRender = nuke.Boolean_Knob("terminal_render", "Render in Terminal")
            self._state.setKnob(self._termRender, False)
            self._termRender.setFlag(nuke.STARTLINE)
            self.addKnob(self._termRender)
            if self._bgRender.value() or self._termRender.value():
                self.bg_render_knobs = True
            else:
                self.bg_render_knobs = False

            self._numInstances = nuke.Int_Knob("num_instances", "Instance Number")
            self._numInstances.setVisible(self.bg_render_knobs)
            self._state.setKnob(self._numInstances, 1)
            self.addKnob(self._numInstances)

            self._numThreads = nuke.Int_Knob("num_threads", "Thread limit")
            self._numThreads.setVisible(self.bg_render_knobs)
            self._state.setKnob(self._numThreads, max(nuke.NUM_CPUS / 2, 1))
            self.addKnob(self._numThreads)

            self._maxMem = nuke.String_Knob("max_memory", "Memory limit")
            self._state.setKnob(self._maxMem, str(max(nuke.memory("max_usage") / 2097152, 16)) + "M")
            self._maxMem.setVisible(self.bg_render_knobs)
            self.addKnob(self._maxMem)

            self._chunkSize = nuke.Int_Knob("chunk_size", "Chunk Size")
            self._chunkSize.setVisible(False)
            self._state.setKnob(self._chunkSize, 4)
            self.addKnob(self._chunkSize)


        def _getBackgroundLimits(self):
            return {
                "maxThreads": self._numThreads.value(),
                "maxCache": self._maxMem.value() }

        def knobChanged(self, knob):
            nukescripts.ExecuteDialog.knobChanged(self, knob)

            if knob == self._bgRender:
                self._termRender.setValue(False)
                # self._tractorRender.setValue(False)
                self._numThreads.setVisible(self._bgRender.value() or self._termRender.value())
                self._maxMem.setVisible(self._bgRender.value() or self._termRender.value())

            if knob == self._termRender:
                self._bgRender.setValue(False)
                # self._tractorRender.setValue(False)
                self._numThreads.setVisible(self._bgRender.value() or self._termRender.value())
                self._maxMem.setVisible(self._bgRender.value() or self._termRender.value())
                self._numInstances.setVisible(self._termRender.value())

        def isBackgrounded(self):
            """Return whether the background rendering option is enabled."""
            return self._bgRender.value()

        def run(self):
            frame_ranges = nuke.FrameRanges(self._frameRange.value().split(','))
            views = self._selectedViews()
            try:
                nuke.Undo().disable()
                if (self.isBackgrounded()):
                    nuke.executeBackgroundNuke(nuke.EXE_PATH, self._nodeSelection, frame_ranges, 
                        views, self._getBackgroundLimits(), continueOnError = self._continueOnError.value())
                elif self._termRender.value():
                    terminal_render(self._nodeSelection, frame_ranges, views, self._numInstances.value(), 
                        self._numThreads.value(), self._maxMem.value())
                else:
                    nuke.executeMultiple(self._nodeSelection, frame_ranges, views, continueOnError = self._continueOnError.value())
            except RuntimeError as e:
                if self._exceptOnError or e.args[0][0:9] != "Cancelled":   # TO DO: change this to an exception type
                    raise
            finally:
                nuke.Undo().enable()


    def render(write_nodes):
        # Render only Write nodes and Groups with a Write node inside
        approved_writes = []
        for write_node in write_nodes:
            if write_node.Class() == 'Group':
                if 'Write' in [n.Class() for n in write_node.nodes()]:
                    approved_writes.append(write_node)
            if write_node.Class() == 'Write':
                approved_writes.append(write_node)
        if approved_writes:
            d = RenderDialog(_dstate, nuke.root(), approved_writes, False)
            if d.showModalDialog() == True:
                nuke.scriptSave()
                d.run()