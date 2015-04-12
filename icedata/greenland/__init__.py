# register the modules
from icedata import _import_modules

__all__ = ["presentday","bamber2013"]
_import_modules(__all__, package='icedata.greenland')
