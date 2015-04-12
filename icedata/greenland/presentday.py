""" Present-day Greenland Dataset 

http://websrv.cs.umt.edu/isis/index.php/Present_Day_Greenland
"""
from __future__ import absolute_import
from os.path import join
import numpy as np
import netCDF4 as nc
import dimarray as da
from icedata.common import ncload as _ncload

NAME = "presentday_greenland"
DESC = __doc__

VARIABLES = ["surface_elevation", "bedrock_elevation", "surface_velocity", "ice_thickness", "surface_elevation_rate"]
GRID_MAPPING = {'ellipsoid': u'WGS84',
     'false_easting': 0.0,
     'false_northing': 0.0,
     'grid_mapping_name': u'polar_stereographic',
     'latitude_of_projection_origin': 90.0,
     'standard_parallel': 71.0,
     'straight_vertical_longitude_from_pole': -39.0}  # in that case, one could just read it from netCDF

RESOLUTION = 5000
VERSION = "v1.1"
_NCFILE = join("greenland", "Present_Day_Greenland","Greenland_5km_{version}.nc")
_map_var_names = {"surface_elevation":"usrf", "bedrock_elevation":"topg", "ice_thickness":"thk", "surface_velocity":"surfvelmag","surface_elevation_rate":"dhdt"}
_map_dim_names = {"x":"x1","y":"y1"}

def load(variables=None, bbox=None, maxshape=None, version=VERSION):
    """Load Present-day Greenland standard dataset

    Examples
    --------
    >>> from icedata.greenland import presentday as pdg
    >>> bbox = [-500e3, 0, -1500e3, -800e3] # (in meters)
    >>> pdg.load()
    >>> pdg.load(bbox)
    """
    # determine the variables to load
    if variables is None:
        variables = VARIABLES
    ncname = _NCFILE.format(version=version)
    data = _ncload(ncname, variables=variables, bbox=bbox, maxshape=maxshape, map_var_names=_map_var_names, map_dim_names=_map_dim_names, time_idx=0)
    data.dataset = NAME
    data.description = DESC
    return data
