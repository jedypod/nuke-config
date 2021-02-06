from builtins import range
import nuke
import math
import os

def simulate():
    origFrame = nuke.frame()
    n = nuke.thisNode()
    frameStart = int(n.knob('start').value())
    frameEnd = int(n.knob('end').value())
    totalFrames = int(frameEnd - frameStart + 1)

    cache_path = n['cache'].value()

    # Must be exr format
    file_dir, ext = os.path.splitext(cache_path)
    if ext != '.exr':
        cache_path = file_dir + '.exr'
        n['cache'].setValue(cache_path)

    # Must have frame numbering
    try:
        existing_simulation = os.path.exists(cache_path % frameStart)
    except TypeError:
        nuke.critical("Simulation cannot be executed for multiple frames.")
        return

    # Warn user if simulation is not going to overwrite
    extend_existing = n.knob('extend_existing').value()
    if extend_existing and not existing_simulation:
        if not nuke.ask("No render on frame <b>%i</b> for sequence:\n\n<i>%s</i>\n\nSequences may not match.\nContinue?" % (frameStart, cache_path)):
            return
    elif existing_simulation and not extend_existing:
        if not nuke.ask("Simulation will overwrite existing sequence:\n\n<i>%s</i>\n\nContinue?" % cache_path):
            return

    # Create directory if it doesn't exist
    directory = os.path.dirname(cache_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    writeWater = n.node('WriteWATER')
    cache = n.node('CACHE')

    task = nuke.ProgressTask("Simulating...")

    try:
        for frame in range(frameStart, frameStart + totalFrames):
            # Update taskbar
            task.setMessage("Frame %i of %i" % (frame, frameStart + totalFrames - 1))
            progress = (float(frame - frameStart) / totalFrames) * 100
            task.setProgress(int(progress))
            # Abort option
            if task.isCancelled():
                nuke.executeInMainThread(nuke.message, args=("Aborted!"))
                break
            # Skip existing frames
            if extend_existing and os.path.exists(cache_path % frame):
                continue
            # Render frame
            nuke.frame(frame)
            cache.knob('reload').execute()
            nuke.execute(writeWater, frame, frame)
    finally:
        del task

    cache.knob('reload').execute()
    nuke.frame(origFrame)
