"""Velocity dataset from Rignot and Mouginot (2012)
"""

import os
import numpy as np
import netCDF4 as nc
import dimarray as da
from icedata.common import get_datafile, get_slices_xy

NAME = __name__
DESC = __doc__
NCFILE = os.path.join("greenland","Rignot_Mouginot_2012_IceFlowGreenlandPolarYear20082009","velocity_greenland_15Feb2013.nc")

GRID_MAPPING = {'ellipsoid': u'WGS84',
         'false_easting': 0.0,
         'false_northing': 0.0,
         'grid_mapping_name': u'polar_stereographic',
         'latitude_of_projection_origin': 90.0,
         'standard_parallel': 70.0,
         'straight_vertical_longitude_from_pole': -45.0}

_MAP_VAR_NAMES = {"surface_velocity_x":"vx", "surface_velocity_y":"vy"}

VARIABLES = sorted(_MAP_VAR_NAMES.keys())

def load_bbox(variables=None, bbox=None, maxshape=None):
    """ load data for a region
    
    Parameters
    ----------
    bbox: left, right, bottom, top (in local coordinate system)
    maxshape: tuple, optional
        maximum shape of the data to be loaded

    Returns
    -------
    NOTE: projection coordinates: lon0=-45, lat0=90, sec_lat=70
    """
    if variables is None:
        variables = VARIABLES

    f = nc.Dataset(get_datafile(NCFILE))

    # reconstruct coordinates
    xmin, ymax = -638000.0, -657600.0
    spacing = 150.0
    nx, ny = 10018, 17946
    x = np.linspace (xmin, xmin + spacing*(nx-1), nx)  # ~ 10000 * 170000 points, 
    y = np.linspace (ymax, ymax - spacing*(ny-1), ny)  # reversed data

    slice_x, slice_y = get_slices_xy((x,y), bbox, maxshape, inverted_y_axis=True)

    vx = f.variables['vx'][slice_y, slice_x]
    vy = f.variables['vy'][slice_y, slice_x]
    x = x[slice_x]
    y = y[slice_y]

    # convert all to a dataset
    ds = da.Dataset()
    for nm in variables:
        ncvar = _MAP_VAR_NAMES[nm]
        ds[nm] = da.DimArray(f.variables[ncvar][slice_y, slice_x], axes=[y,x], dims=['y','x'])
        # attributes
        for att in f.variables[ncvar].ncattrs():
            setattr(ds[nm], att.lower(), f.variables[ncvar].getncattr(att))

    # attributes
    for att in f.ncattrs():
        setattr(ds, att.lower(), f.getncattr(att))

    ds.dataset = NCFILE
    ds.description = DESC

    f.close()

    return ds
