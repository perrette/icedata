""" Present-day Greenland Dataset 

http://websrv.cs.umt.edu/isis/index.php/Present_Day_Greenland
"""
from __future__ import absolute_import
from os.path import join
import numpy as np
import netCDF4 as nc
import dimarray as da
from icedata.settings import DATAROOT
from icedata.common import get_slices_xy

NAME = "presentday_greenland"
VERSION = "v1.1"
_basename = "Greenland_5km_v{version}.nc"
_NCFILE = join(DATAROOT, "greenland", "Present_Day_Greenland",_basename)
VARIABLES = ["surface_elevation", "bedrock_elevation", "surface_velocity", "ice_thickness", "surface_elevation_rate"]
GRID_MAPPING = {'ellipsoid': u'WGS84',
     'false_easting': 0.0,
     'false_northing': 0.0,
     'grid_mapping_name': u'polar_stereographic',
     'latitude_of_projection_origin': 90.0,
     'standard_parallel': 71.0,
     'straight_vertical_longitude_from_pole': -39.0}  # in that case, one could just read it from netCDF

_namelookup = {"surface_elevation":"usrf", "bedrock_elevation":"topg", "ice_thickness":"thk", "surface_velocity":"surfvelmag","surface_elevation_rate":"dhdt"}

def load_bbox(bbox=None, variables=None, maxshape=None, version=VERSION):
    # determine the variables to load
    if variables is None:
        variables = VARIABLES
    ncvariables = [_namelookup[nm] for nm in variables]

    # open the netCDF dataset
    nc_ds = nc.Dataset(_NCFILE.format(version))

    # determine the indices to extract
    x = nc_ds.variables['x1']
    y = nc_ds.variables['y1']
    slice_x, slice_y = get_slices_xy(xy=(x, y), bbox=bbox, maxshape=maxshape)

    # load the data using dimarray (which also copy attributes etc...)
    data = da.read_nc(nc_ds, ncvariables, indices={'x1':slice_x,'y1':slice_y, 'time':0}, indexing='position')

    # close dataset
    nc_ds.close()

    # rename dimensions appropriately and set metadata
    data.dims = ('y','x') 
    data.rename_keys({ncvar:var for var, ncvar in zip(variables, ncvariables)}, inplace=True)
    data.grid_mapping = GRID_MAPPING  # if not already present in the netCDF
    data.dataset = NAME 

    return data
