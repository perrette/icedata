""" Bedrock elevation
"""
import os
from icedata.common import ncload_bbox as _ncload_bbox

# NCFILE = os.path.join(datadir, "MCdataset-2014-10-16.nc")
NCFILE = os.path.join("greenland","MCdataset-2014-10-16.nc")

NAME = __name__
DESC = __doc__

GRID_MAPPING = {'ellipsoid': u'WGS84',
         'false_easting': 0.0,
         'false_northing': 0.0,
         'grid_mapping_name': u'polar_stereographic',
         'latitude_of_projection_origin': 90.0,
         'standard_parallel': 70.0,
         'straight_vertical_longitude_from_pole': -45.0}

_MAP_VAR_NAMES = {"surface_elevation":"surface", 
                  "bedrock_elevation":"bed", 
                  "ice_thickness":"thickness", 
                  "bedrock_elevation_error":"errbed",
                  }

VARIABLES = sorted(_MAP_VAR_NAMES.keys())
RESOLUTION = 150

def load_bbox(bbox=None, variables=None, maxshape=None):
    """Load Bamber et al 2013 elevation dataset
    """
    # determine the variables to load
    if variables is None:
        variables = VARIABLES

    # need to read the variables independently
    data = _ncload_bbox(NCFILE, variables=variables, bbox=bbox, maxshape=maxshape, map_var_names=_MAP_VAR_NAMES, inverted_y_axis=True)
    data.dataset = NAME
    return data
