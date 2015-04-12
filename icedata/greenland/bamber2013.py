"""Bamber et al 2013
"""
import os
import numpy as np
import netCDF4 as nc
from icedata.common import ncload as _ncload, get_datafile as _get_datafile, get_slices_xy

#ncfile = datadir+'bamber_2013_1km/Greenland_bedrock_topography_V2.nc'
NCFILE = os.path.join('greenland','bamber_2013_1km','Greenland_bedrock_topography_V3.nc')

NAME = __name__
DESC = __doc__

GRID_MAPPING = {'ellipsoid': u'WGS84',
         'false_easting': 0.0,
         'false_northing': 0.0,
         'grid_mapping_name': u'polar_stereographic',
         'latitude_of_projection_origin': 90.0,
         'standard_parallel': 71.0,
         'straight_vertical_longitude_from_pole': -39.0}

# just for standard names
_MAP_VAR_NAMES = {"surface_elevation":"SurfaceElevation", 
                  "bedrock_elevation":"BedrockElevation", 
                  "ice_thickness":"IceThickness", 
                  "surface_elevation_error":"SurfaceRMSE",
                  "bedrock_elevation_error":"BedrockError",
                  }

VARIABLES = sorted(_MAP_VAR_NAMES.keys())
RESOLUTION = 1000


def load(variables=None, bbox=None, maxshape=None, processed=True):
    """Load Bamber et al 2013 elevation dataset
    """
    map_var_names = _MAP_VAR_NAMES.copy()
    if not processed:
        map_var_names['bedrock_elevation'] = map_var_names['bedrock_elevation_unprocessed']
        map_var_names['surceface_elevation'] = map_var_names['surceface_elevation_unprocessed']

    # determine the variables to load
    if variables is None:
        variables = VARIABLES

    # need to read the variables independently
    ncfile = _get_datafile(NCFILE)
    with nc.Dataset(ncfile) as ds:
        x = ds.variables['projection_x_coordinate'][:]
        y = ds.variables['projection_y_coordinate'][:]

    data = _ncload(NCFILE, variables=variables, bbox=bbox, maxshape=maxshape, map_var_names=map_var_names, x=x, y=y)
    data.dataset = NAME 
    return data
