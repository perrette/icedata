"""Velocity dataset from Rignot and Mouginot (2012)
"""

import os
import numpy as np
import netCDF4 as nc
import dimarray as da
from icedata.common import get_datafile, get_slices_xy, check_variables

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

VARIABLES = sorted(_MAP_VAR_NAMES.keys()) + ["surface_velocity"]

def load(variables=None, bbox=None, maxshape=None):
    """ load data for a region
    
    Parameters
    ----------
    variables : variables to load
    bbox: left, right, bottom, top (in local coordinate system)
    maxshape: tuple, optional
        maximum shape of the data to be loaded

    Returns
    -------
    NOTE: projection coordinates: lon0=-45, lat0=90, sec_lat=70
    """
    if variables is None:
        variables = VARIABLES
    variables, _variable = check_variables(variables)

    if 'surface_velocity' in variables:
        # make sure the component are included
        surfvel = True
        add_vars = ["surface_velocity_x", "surface_velocity_y"]
        added_vars = []
        variables = [v for v in variables] # copy
        for v in add_vars:
            if v not in variables:
                variables.append(v)
                added_vars.append(v)
        variables.remove("surface_velocity")
    else:
        surfvel = False

    ds = _load(variables, bbox, maxshape)

    # now compute velocity magnitude
    if surfvel:
        ds["surface_velocity"] = np.sqrt(np.square(ds["surface_velocity_x"]) + np.square(ds["surface_velocity_y"]))
        ds["surface_velocity"].units = ds["surface_velocity_x"].units
        ds["surface_velocity"].long_name = "Surface Velocity Magnitude"
        for v in added_vars:
            del ds[v] # demove variable

    if _variable:
        ds = ds[_variable]

    return ds


def _load(variables, bbox=None, maxshape=None):
    """
    """
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
    _map_var_names = _MAP_VAR_NAMES.copy()
    for nm in variables:
        ncvar = _map_var_names.pop(nm,nm)
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
