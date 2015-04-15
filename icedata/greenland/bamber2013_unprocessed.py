"""Just like Bamber et al 2013, but load unprocessed data by default
"""
from functools import partial

from .bamber2013 import *
load_orig = load
load = partial(load_orig, processed=False)
