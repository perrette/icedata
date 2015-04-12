import dimarray as da
import numpy as np

def get_slices_xy(xy, bbox, maxshape):
    x, y = xy
    # determine start and stop indices form bounding box
    if bbox is not None:
        l, r, b, t = bbox  # in meters
        startx, stopx = np.searchsorted(x[:], [l, r])
        starty, stopy = np.searchsorted(y[:], [b, t])
    else:
        startx, stopx = 0, x.size-1
        starty, stopy = 0, y.size-1
    nx = (stopx-startx+1)
    ny = (stopy-starty+1)
    # sub-sample dataset if it exceeds maximum desired shape
    if maxshape is not None:
        shapey, shapex = maxshape
        stepy = int(ny/shapey)
        stepx = int(nx/shapex)
    else:
        stepy = stepx = None
    slice_x = slice(startx, stopx, stepx)
    slice_y = slice(starty, stopy, stepy)
    return slice_x, slice_y

# function factory to create a load path function from load_bbox
def create_load_path(load_bbox):
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
        data2d = load_bbox(variables=variables, bbox=[l, r, b, t])
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
