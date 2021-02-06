'''
Rolling autosave.
Original version : nukescripts/rollingAutoSave.py
Modified to put all autosave files in <scriptdir>/autosaves folder,
to number with 2 digits padding and to have 14 backup files max.
'''

import os
import glob
import time

import nuke


def fixAutosavePath(filename):
    '''Force a specific subfolder in the autosave path.
    This is done here to avoid messing with the autosave path preference.'''
    subfolder = 'autosaves'
    dirname, basename = os.path.split(filename)
    if os.path.basename(dirname) != subfolder:
        filename = os.path.join(dirname, subfolder, basename)
    return filename


def onAutoSave(filename):
    '''Rolling autosave.'''
    # Ignore untitled autosave
    if nuke.root().name() == 'Root':
        return filename

    filename = fixAutosavePath(filename)

    # Make autosave dir if it doesn't exist
    autosave_dir = os.path.dirname(filename)
    if not os.path.exists(autosave_dir):
        try:
            os.makedirs(autosave_dir)
        except OSError as err:
            if err.errno == 13:
                return filename

    file_number = 0
    files = getAutoSaveFiles(filename)

    if len(files) > 0:
        lastFile = files[-1]

        # Get the last file number
        if len(lastFile) > 0:
            try:
                file_number = int(lastFile[-2:])
            except ValueError:
                pass
            file_number += 1

    # Set number of autosave backups to use
    if file_number > 14:
        file_number = 0

    filename = filename + '{0:02d}'.format(file_number)

    return filename


def onAutoSaveRestore(filename):
    '''Restore most recent autosave.'''
    files = getAutoSaveFiles(filename)
    if len(files) > 0:
        filename = files[-1]
    return filename


def onAutoSaveDelete(filename):
    '''Only delete untitled autosave.'''
    if nuke.root().name() == 'Root':
        return filename

    # Return None here to not delete auto save file
    return None


def getAutoSaveFiles(filename):
    '''Get all autosave files that exist, sorted by date modified.'''
    date_file_list = []

    filename = fixAutosavePath(filename)
    files = glob.glob(filename + '[0-9]' * 2)
    files.extend(glob.glob(filename))

    for path in files:
        # retrieves the stats for the current file as a tuple
        # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        # the tuple element mtime at index 8 is the last-modified-date
        stats = os.stat(path)
        # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
        # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
        # note:  this tuple can be sorted properly by date and time
        lastmod_date = time.localtime(stats[8])
        # create list of tuples ready for sorting by date
        date_file_tuple = lastmod_date, path
        date_file_list.append(date_file_tuple)

    date_file_list.sort()
    return [filename for _, filename in date_file_list]



# Register the autosave callbacks.
nuke.addAutoSaveFilter(onAutoSave)
nuke.addAutoSaveRestoreFilter(onAutoSaveRestore)
nuke.addAutoSaveDeleteFilter(onAutoSaveDelete)
