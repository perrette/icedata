""" Read CRESIS data
"""
import os
import numpy as np
import pandas as pd

import cartopy.crs as ccrs
import dimarray.geo as da
from dimarray.geo.crs import get_crs

from icedata.settings import DATAROOT
#from grids import proj, proj_cresis

CRESIS_DIR = os.path.join(DATAROOT, "greenland", "BasalTopographyCresis/")

MAPPING = {'ellipsoid': u'WGS84',
         'false_easting': 0.0,
         'false_northing': 0.0,
         'grid_mapping_name': u'polar_stereographic',
         'latitude_of_projection_origin': 90.0,
         'standard_parallel': 70.0,
         'straight_vertical_longitude_from_pole': -45.0}

__all__ = ['load','load_error', 'variables','help']

def glaciers():
    return ['petermann', 'helheim', 'jakobshavn', 'kangerdlugssuaq', 'kogebugt','nwcoast','79n']

def is_defined(name):
    return name.lower() in glacier()

def get_fname(name, kind='grids'):
    """ return file name corresponding to a particular Cresis data file
    """
    if 'petermann' in name.lower():
        name2 = 'Petermann_2010_2012_Composite'
    elif 'jakobshavn' in name.lower():
        name2 = 'Jakobshavn_2006_2012_Composite'
    elif 'kangerdlugssuaq' in name.lower():
        name2 = 'Kangerdlugssuaq_2008_2012_Composite'
    elif 'helheim' in name.lower():
        name2 = 'Helheim_2008_2012_Composite'
    elif 'kogebugt' in name.lower():
        name2 = 'KogeBugt_2009_2011_Composite'
    elif 'nwcoast' in name.lower():
        name2 = 'NWCoast_2010_2011_Composite'
    elif '79n' in name.lower():
        name2 = '79N_2010_2011_Composite'

    else:
        raise Exception('unknown glacier name in CRESIS: '+name)

    if kind == 'grids':
        fname = os.path.join(CRESIS_DIR,name2,kind,name2+'_XYZGrid.txt')
    elif kind == 'grids_coord':
        # file needed to get interpolation grid
        fname = os.path.join(CRESIS_DIR,name2,'grids',name2+'_Surface.txt')
    elif kind == 'errors':
        fname = os.path.join(CRESIS_DIR,name2,kind,name2+'_Crossovers.csv')
    else:
        raise Exception('unknown kind of file: '+kind)

    return fname

def read_xyz_composite(filein):
    """ Read lon, lat, thickness, surface and bottom topography as DataFrame

    e.g. for Petermann: grids/Petermann_2010_2012_Composite_XYZGrid.txt
    """
    # read data
    data = pd.DataFrame.from_csv(filein).reset_index()
    # filled the missing values with NaN
    data = data.replace(-9999, np.nan)
    return data


def reshape_xyz(x, y, *args):
    """ Reshape xyz data for a given variable onto a 2D map

    Note first index is for lat (y), second for lon (x)
    """
    # Find dimensions:
    # x (lon): nj
    # y (lat): ni
    # => fastest moving coordinates?

    # x(nj) is slow moving: y(ni) given by x's first change
    if x[1] - x[0] == 0:  
        nj = np.where(np.abs(np.diff(x)) > 0)[0][0]+1
        ni = np.size(x)/nj 

    # y is slow moving
    else:
        ni = np.where(np.abs(np.diff(y)) > 0)[0][0]+1
        nj = np.size(y)/ni 

    # return reshaped variables as, [x, y, arg1, arg2...]
    return [np.reshape(v,(ni, nj)).T[::-1] for v in [x,y]+list(args)]

def load(name):
    """ Load cresis data

    Returns a Dataset of variables
    """
    data = read_xyz_composite(get_fname(name))

    # 1D => 2D conversion for all variables of interest
    x, y, z, h, s = reshape_xyz(data['LON'].values,data['LAT'].values, data['BOTTOM'].values, data['THICK'].values, data['SURFACE'].values)

    # mapping according to netCDF conventions
    ds = da.Dataset()

    x0 = x[0]
    y0 = y[:,0]

    ds['zb'] = da.GeoArray(z, axes=[('y',y0),('x',x0)], grid_mapping='mapping')
    ds['h'] = da.GeoArray(h, axes=[('y',y0),('x',x0)], grid_mapping='mapping')
    ds['zs'] = da.GeoArray(s, axes=[('y',y0),('x',x0)], grid_mapping='mapping')
    null = da.GeoArray('')
    null.mapping = MAPPING
    ds['mapping'] = null

    ds.glacier_name = 'Petermann'
    ds.dataset = 'CRESIS'

    return ds

def read_thickness_error(filein):
    """
    e.g. for Petermann: errors/Petermann_2010_2012_Composite_Crossovers.csv
    """
    data = pd.DataFrame.from_csv(filein).reset_index()
    lon = data['LONA'].values 
    lat = data['LATA'].values 
    e = data['THICKB'].values - data['THICKA'].values # thickness error from cross-over analysis
    return lon, lat, np.abs(e)
    
def map_error(x, y, e, xi, yi):
    """ map trajectories onto a 2D grid for comparison with other variables
    """
    if 0:
        from matplotlib.mlab import griddata
        ei = griddata(x, y, e, xi, yi) # quite clean
        return ei

    else: # => here that is what is used
        from scipy.interpolate import griddata
        xy = np.vstack((x, y)).T 
        ei = griddata(xy, e, (xi, yi), method='nearest') # use nearest neighbour interp because more along-flow structure
        return ei

def load_grid(name):
    """ Load Cresis grid """

    fname = get_fname(name, 'grids_coord')
    f = open(fname)
    _, ncols = f.readline().strip().split() ; ncols = int(ncols)
    _, nrows = f.readline().strip().split() ; nrows = int(nrows)
    _, xllcorner = f.readline().strip().split() ; xllcorner = float(xllcorner)
    _, yllcorner = f.readline().strip().split() ; yllcorner = float(yllcorner)
    _, cellsize = f.readline().strip().split() ; cellsize = float(cellsize)
    f.close()
    xi = np.linspace(xllcorner, xllcorner+(ncols-1)*cellsize, ncols)
    yi = np.linspace(yllcorner, yllcorner+(nrows-1)*cellsize, nrows)
    #xi, yi = np.meshgrid(xi, yi)
    return xi, yi

def load_error(name):
    """ load thickness error interpolated consistently with the rest of data
    """
    fname = get_fname(name, kind='errors')
    lon, lat, e = read_thickness_error(fname)
    # now convert lon/lat to x,y
    prj = get_crs(MAPPING) # get projection
    x, y, z = prj.transform_points(ccrs.Geodetic(), lon, lat).T
    xi, yi = load_grid(name)
    xi2, yi2 = np.meshgrid(xi, yi)
    ei = map_error(x, y, e, xi2, yi2)
    return da.GeoArray(ei, axes=[('y',yi),('x',xi)], grid_mapping=MAPPING)

