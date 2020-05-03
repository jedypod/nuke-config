import nuke
import os


thisdir = os.path.dirname(__file__)
modules = [f.split('.py')[0] for f in os.listdir(thisdir) if f.endswith('.py') and '__init__.py' not in f]
dirs = [d for d in os.listdir(thisdir) if os.path.isdir(os.path.join(thisdir, d)) and '__init__.py' in os.listdir(os.path.join(thisdir, d))]

# modules += dirs

for module in modules:
    try:
        __import__(module, locals(), globals())
    except Exception as exc:
        nuke.tprint('Exception occured loading module \n\t{0}\n\t{1}\n\tContinueing startup...'.format(module, exc))
        pass
del module