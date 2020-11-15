import nuke
import os

# Module to contain all User-Interface code and tools
# Auto-import all working python files in this folder # https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder


for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except Exception as exc:
        nuke.tprint('Exception occured loading module \n\t{0}\n\t{1}\n\tContinueing startup...'.format(module[:-3], exc))
        pass

del module