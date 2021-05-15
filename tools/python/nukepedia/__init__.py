from __future__ import absolute_import
import nuke
import os
import pkgutil

'''
    nukepedia module

    __all__ is defined automatically for all submodules of this module
    https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
'''

__all__ = list(module for _, module, _ in pkgutil.iter_modules(
    [os.path.dirname(__file__)]))