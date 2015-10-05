from __future__ import division
from os import path
import numpy as np
import netCDF4 as nc
import dimarray as da
from . import settings

def transform_bbox(bbox, grid_mapping1, grid_mapping2):
    # get CARTOPY classes from C.F.1-6 convention
    from dimarray.geo.crs import get_crs
    crs1 = get_crs(grid_mapping1)
    crs2 = get_crs(grid_mapping2)
    # make a fake grid to transform
    l, r, b, t = bbox
    x1, y1 = np.meshgrid(np.linspace(l, r, 10), np.linspace(b,t,10))
    xyz = crs2.transform_points(crs1, x1, y1)
    x2 = xyz[...,0]
    y2 = xyz[...,1]
    l2 = np.min(x2)
    r2 = np.max(x2)
    b2 = np.min(y2)
    t2 = np.max(y2)
    return l2, r2, b2, t2

def get_slices_xy(xy, bbox, maxshape, inverted_y_axis):
    """Return indexing slices along x and y.

    Accounts for bounding box, maxshape not to exceep, inverted y axis...
    """
    x, y = xy
    if inverted_y_axis:
        y = y[::-1]
    # determine start and stop indices form bounding box
    if bbox is not None:
        l, r, b, t = bbox  # in meters
        startx, stopx = np.searchsorted(x[:], [l, r])
        startx = min(startx, x.size-1)
        starty, stopy = np.searchsorted(y[:], [b, t])
        starty = min(starty, y.size-1)
    else:
        startx, stopx = 0, x.size
        starty, stopy = 0, y.size
    # sub-sample dataset if it exceeds maximum desired shape
    if maxshape is not None:
        shapey, shapex = maxshape
        stepy = max(1, int(y.size//shapey)) # step 0 forbidden
        stepx = max(1, int(x.size//shapex))  
    else:
        stepy = stepx = 1
    slice_x = slice(startx, stopx, stepx)
    # invert sampling ?
    if inverted_y_axis:
        slice_y = slice(y.size-starty, y.size-stopy, -stepy)
    else:
        slice_y = slice(starty, stopy, stepy)
    return slice_x, slice_y

def get_datafile(ncfile, dataroot=None):
    if dataroot is None:
        dataroot = settings.DATAROOT
    return path.join(dataroot, ncfile)

def check_variables(variables):
    if isinstance(variables, basestring):
        variable = variables
        variables = [variable]
    else:
        variable = None
    return variables, variable

def ncload(ncfile, variables=None, bbox=None, maxshape=None, map_var_names=None, map_dim_names=None, time_idx=None, time_dim='time', inverted_y_axis=False, dataroot=None, x=None, y=None, xdim='x', ydim='y'):
    """Standard ncload for netCDF files

    Parameters
    ----------
    map_var_name : None or dict-like : make standard variables and actual file variables names match
    map_dim_name : None or dict-like : make standard dimensions and actual file dimensions names match
    inverted_y_axis : deal with the case where y axis is inverted (Rignot and Mouginot, Morlighem...)
    time_idx, time_dim : can be provided to extract a time slice
    dataroot : provide an alternative root path for datasets
    x, y : array-like : provide coordinates directly, when not present in file.
    """
    ncfile = get_datafile(ncfile, dataroot)
    variables, _variable = check_variables(variables)

    # determine the variables to load
    if map_var_names is not None:
        map_var_names = map_var_names.copy() # becaause of pop
        ncvariables = [map_var_names.pop(nm,nm) for nm in variables]
    else:
        ncvariables = variables

    if map_dim_names is not None:
        xnm = map_dim_names[xdim]
        ynm = map_dim_names[ydim]
    else:
        xnm = xdim
        ynm = ydim

    # open the netCDF dataset
    nc_ds = nc.Dataset(ncfile)

    external_axes = x is not None or y is not None
    if x is None:
        x = nc_ds.variables[xnm]
    if y is None:
        y = nc_ds.variables[ynm]

    # determine the indices to extract
    slice_x, slice_y = get_slices_xy(xy=(x, y), bbox=bbox, maxshape=maxshape, inverted_y_axis=inverted_y_axis)
    indices = {xnm:slice_x,ynm:slice_y}
    if time_idx is not None:
        indices[time_dim] = time_idx

    # load the data using dimarray (which also copy attributes etc...)
    data = da.read_nc(nc_ds, ncvariables, indices=indices, indexing='position')

    # close dataset
    nc_ds.close()

    # in case axes were provided externally, just replace the values
    if external_axes:
        data.axes[xnm][:] = x[slice_x]
        data.axes[ynm][:] = y[slice_y]

    # rename dimensions appropriately and set metadata
    if map_dim_names is not None:
        if data.dims == (xnm, ynm):
            data.dims = (xdim, ydim)
        elif data.dims == (ynm, xnm):
            data.dims = (ydim, xdim)
        # unknown case? do nothing

    # rename variable names
    if map_var_names is not None:
        data.rename_keys({ncvar:var for var, ncvar in zip(variables, ncvariables)}, inplace=True)

    # only one variable
    if _variable is not None:
        data = data[_variable]

    return data

# function factory to create a load path function from load
# REMOVE???
def create_load_path(load_map_func):
    def load_path(path, variables=None, method="after"):
        """Load variables along a path

        Parameters
        ----------
        path : list of [(x0,y0), (x1, y1), ...] coordinates
        variables : list, optional
            of variables to be loaded (by default, all in a dataset)
        method : str, optional
            method to sample the data, by default "after", which indicates
            the grid point at or just after the match, as returned
            by searchsorted
        """
        if method == "after":
            pass
        elif method == "nearest":
            raise NotImplementedError()
        elif method == "linear":
            raise NotImplementedError()
        else:
            raise ValueError("Invalid method: "+method)
        xs, ys = zip(*path) # [(x0, y0), (x1, ...)] into [[x0,x1..], [y0, y1..]]
        xs = np.asarray(xs)
        ys = np.asarray(ys)
        l = np.min(xs)
        r = np.max(xs)
        b = np.min(ys)
        t = np.max(ys)
        data2d = load_map_func(variables=variables, bbox=[l, r, b, t])
        # add a new coordinate s
        diff_s = np.sqrt(np.square(np.diff(xs)) + np.square(np.diff(ys)))
        s = np.concatenate(([0], np.cumsum(diff_s)))
        datapath = da.Dataset()
        # add x and y as variables in the dataset
        datapath['x'] = da.DimArray(xs, axes=[s], dims=['s'])
        datapath['x'].long_name = "x-coordinate along sample path"
        datapath['y'] = da.DimArray(ys, axes=[s], dims=['s'])
        datapath['y'].long_name = "y-coordinate along sample path"
        # now extract dataset...
        i = np.searchsorted(data2d.y, ys)
        j = np.searchsorted(data2d.x, xs)
        i[i==data2d.y.size] -= 1 # out-of-bound 
        j[j==data2d.x.size] -= 1
        for v in data2d.keys():
            pathvals = data2d[v].values[i,j]
            datapath[v] = da.DimArray(pathvals, axes=[s], dims=['s'])
            datapath[v].attrs.update(data2d[v].attrs)
        return datapath
    return load_path
