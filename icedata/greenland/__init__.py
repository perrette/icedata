# register the modules
from icedata import _import_modules

__all__ = ["presentday"]
_import_modules(__all__, package='icedata.greenland')
