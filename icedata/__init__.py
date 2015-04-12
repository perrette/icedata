from __future__ import print_function, absolute_import
from importlib import import_module  # generic module import (builtin)
import warnings
from . import common
from . import settings

def setup(datadir):
    """ Define an alternative setup directory
    """
    settings.DATAROOT=datadir

# register the modules (to be called from within greenland, antarctica)
def _import_modules(modules, package=None, raise_error=True):

    # import all modules and redefine missing functions
    for mod in modules:
        # try to load module
        try:
            m = import_module("."+mod, package=package) # import module by name
        except ImportError as error:
            if raise_error:
                raise
            else:
                warnings.warn(error.message)
                print(error.message)
                continue

        # Add a few hand functions, if missing
        if not hasattr(m, 'load_path'):
            m.load_path =  common.create_load_path(m.load)
