from __future__ import with_statement
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os, sys
import subprocess, shlex
import argparse
import tempfile
sys.path.insert(0, '/usr/lib64/python2.7/site-packages/')
import numpy as np
from libtiff import TIFF
import nuke


from sys import platform as __platform
if __platform == "linux" or __platform == "linux2":
    _platform = 'linux'
elif __platform == "darwin":
    _platform = 'osx'
elif __platform == "win32":
    _platform = 'win'


def frames_to_tc(total_frames, frame_rate):
    fps_int = int(round(frame_rate))
    smpte_token = ":"
    hours = int(total_frames / (3600 * fps_int))
    minutes = int(total_frames / (60 * fps_int) % 60)
    seconds = int(total_frames / fps_int % 60)
    frames = int(total_frames % fps_int)
    return "%02d:%02d:%02d%s%02d" % (hours, minutes, seconds, smpte_token, frames)

def terminal_render():
    parser = argparse.ArgumentParser(description='Render from Nuke to ffmpeg.')
    parser.add_argument("nuke_script",
                        help="Nuke script to render.")
    parser.add_argument("-X", "--write",
                        help="Name of the WriteFFMPEG node to render.")
    parser.add_argument("-F", "--framerange",
                        help="framerange to render. Please specify <start>-<end>.",
                        required=False)
    parser.add_argument("-o", "--output",
                        help="Output qt to render to. Will use the value of the file knob on the WriteFFMPEG node if not specified.",
                        required=False)
    args = parser.parse_args()
    nuke_script = args.nuke_script
    nuke.scriptOpen(nuke_script)
    node = nuke.toNode(args.write)
    node.begin()
    write = nuke.toNode('write_tmp')
    if args.framerange and "-" in args.framerange:
        fr = nuke.FrameRange()
        fr.setLast(int(args.framerange.split('-')[-1]))
        fr.setFirst(int(args.framerange.split('-')[0]))
    else:
        node_framerange = node['framerange'].getValue()
        if node_framerange and "-" in node_framerange:
            fr = nuke.FrameRange()
            fr.setLast(int(node_framerange.split('-')[-1]))
            fr.setFirst(int(node_framerange.split('-')[0]))
        else:
            fr = node.frameRange()

    tmpimg = tempfile.mkstemp('.tiff', "ffmpeg_temp_")[1]
    write['file'].setValue(tmpimg)
    framerate = node['framerate'].getValue()
    output = node['file'].getValue()
    tc = frames_to_tc(fr.first(), framerate)
    ffmpeg_args = "ffmpeg -hide_banner -loglevel info -y \
        -f rawvideo -pixel_format rgb48le -video_size {0}x{1} \
        -framerate {2} -i pipe:0 -timecode {3} {4} {5}".format(
            node.width(), node.height(), framerate, tc,
            node['ffmpeg_args'].getValue(), output)
    print(ffmpeg_args)
    ffproc = subprocess.Popen(
        shlex.split(ffmpeg_args),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
        )
    for i, f in enumerate(fr):
        nuke.execute(write, f, f)
        print("Rendering frame \t{0} of {1}".format(i, fr.frames()))
        img = TIFF.open(tmpimg, mode='r')
        img = img.read_image()
        img.tofile(ffproc.stdin)
        os.remove(tmpimg)
    result, error = ffproc.communicate()

if __name__=="__main__":
    terminal_render()


def prep():
    nuke.scriptSave()
    node = nuke.thisNode()
    ffpy = __file__
    ffpy = ffpy.replace('pyc', 'py')
    node_framerange = node['framerange'].getValue()

    nk_cmd = "{0} -t {1} {2} --write {3} --output {4}".format(
        nuke.EXE_PATH,
        ffpy,
        nuke.root().knob("name").value(),
        node.fullName(),
        node['file'].getValue())
    print("RENDER COMMAND:\n\t{0}".format(nk_cmd))
    if _platform == "win":
        nuke.message("Windows not supported.")
        return
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
        cmd = 'gnome-terminal -e "bash -c \\"{0}; exec bash\\""'.format(nk_cmd)
        #cmd = 'gnome-terminal -e "bash -c \\"{0}\\""'.format(nk_cmd)
    subprocess.Popen(cmd, shell=True)