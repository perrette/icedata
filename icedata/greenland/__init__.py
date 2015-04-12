# register the modules
from icedata import _import_modules

__all__ = ["presentday","bamber2013","morlighem2014", "rignot_mouginot2012"]
_import_modules(__all__, package='icedata.greenland')
