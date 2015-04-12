""" Present-day Greenland Dataset 

http://websrv.cs.umt.edu/isis/index.php/Present_Day_Greenland
"""
from __future__ import absolute_import
from os.path import join
import numpy as np
import netCDF4 as nc
import dimarray as da
from icedata.settings import DATAROOT
from icedata.common import ncload_bbox as _ncload_bbox

NAME = "presentday_greenland"
VERSION = "v1.1"
RESOLUTION = 5000
_NCFILE = join("{dataroot}", "greenland", "Present_Day_Greenland","Greenland_5km_{version}.nc")
VARIABLES = ["surface_elevation", "bedrock_elevation", "surface_velocity", "ice_thickness", "surface_elevation_rate"]
GRID_MAPPING = {'ellipsoid': u'WGS84',
     'false_easting': 0.0,
     'false_northing': 0.0,
     'grid_mapping_name': u'polar_stereographic',
     'latitude_of_projection_origin': 90.0,
     'standard_parallel': 71.0,
     'straight_vertical_longitude_from_pole': -39.0}  # in that case, one could just read it from netCDF

_map_var_names = {"surface_elevation":"usrf", "bedrock_elevation":"topg", "ice_thickness":"thk", "surface_velocity":"surfvelmag","surface_elevation_rate":"dhdt"}
_map_dim_names = {"x":"x1","y":"y1"}

def load_bbox(bbox=None, variables=None, maxshape=None, version=VERSION):
    """Load Present-day Greenland standard dataset

    Examples
    --------
    >>> from icedata.greenland import presentday as pdg
    >>> bbox = [-500e3, 0, -1500e3, -800e3] # (in meters)
    >>> pdg.load_bbox()
    """
    # determine the variables to load
    if variables is None:
        variables = VARIABLES
    ncname = _NCFILE.format(version=version, dataroot=DATAROOT)
    data = _ncload_bbox(ncname, variables=variables, bbox=bbox, maxshape=maxshape, map_var_names=_map_var_names, map_dim_names=_map_dim_names, time_idx=0)
    data.grid_mapping = GRID_MAPPING  # if not already present in the netCDF
    data.dataset = NAME 
    return data
