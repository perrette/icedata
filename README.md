# icedata
python repository to read ice data from various sources and return it in a standardized way


Getting started
---------------

The following code:

    import icedata.greenland as grl
    z = grl.bamber2013.load('surface_elevation')
    print z
    
...will print the representation of a [dimarray](github.com/perrette/dimarray):

    dimarray: 7318894 non-null elements (186607 null)
    0 / y (3001): -3500000.0 to -500000.0
    1 / x (2501): -1300000.0 to 1200000.0
    array(...)
    
To access the unerlying numpy array:

    z.x   # x-coordinate
    z.y   # y-coordinate
    z.values  # underlying data, equivalent to numpy.asarray(z)
    
and metadata:

    z.attrs  # dictionary of metadata
    print z.summary()   # formatted print

See also [dimarray's doc](http://dimarray.readthedocs.org) for more in-depth explanations about this convenient data format.
    
A few standard names are given across the datasets, so that whenever the variable is present,
whatever its name, the corresponding variable will be known.

- bedrock_elevation
- surface_elevation
- surface_elevation_error
- surface_velocity
- surface_velocity_error
    
For instance:

    grl.presentday.load('surface_elevation')
    grl.bamber2013.load('surface_elevation')
    grl.morlighem2014.load('surface_elevation')

...will all work.

But you can still access the variables via their original name as present in the netCDF file (if any):

    grl.presentday.load('usrf')
    grl.bamber2013.load('SurfaceElevation')
    grl.morlighem2014.load('surface')
    
It is possible to provide a bounding box to load only a portion of the data:

    grl.rignot_mouginot2012.load('surface_velocity', bbox=[-350e3, 50e3, -1500e3, -901e3])
    
bbox is lon_w, lon_e, lat_s, lat_n, in meters in the coordinate system the data is defined on.
`icedata` provides a method to transform the bounding box between coordinate systems, 
based on cartopy and dimarray: 

    from icedata.common import transform_bbox
    bbox2 = transform_bbox(bbox, grl.rignot_mouginot2012.GRID_MAPPING, grl.bamber2013.GRID_MAPPING)
    
Note that for convenience the grid mapping is defined in each dataset as a dictionary in a GRID_MAPPING variable. 
To transform the datasets after loading, please see [dimarray documentation on grid projections](http://dimarray.readthedocs.org/en/latest/_notebooks_rst/projection.html#projection).

Additionally, it is possible to sub-sample the data at a lower resolution by passing the `maxshape` variable:

    grl.bamber2013.load('surface_elevation', maxshape=(400,400))
    
...which will return (to be compared to 3001x2501 in the first example above):
    
    dimarray: 174433 non-null elements (4460 null)
    0 / y (429): -3500000.0 to -504000.0
    1 / x (417): -1300000.0 to 1196000.0
    array(...)

    
Dependencies
------------
- numpy [1.9.2]
- [netCDF4](https://github.com/Unidata/netcdf4-python) [1.1.7] - [see instructions here](https://github.com/perrette/python-install/blob/master/README.md#netcdf4)
- [dimarray (dev)](https://github.com/perrette/dimarray) [0.1.9.dev-852f76e]: please install the latest version from github. The pip version will not work  
- [cartopy](https://github.com/SciTools/cartopy) [0.11.0]: used for grid projections, [see instructions here](https://github.com/perrette/python-install/blob/master/README.md#cartopy)


Datasets
--------
Not provided here ! You need to get it yourself...

- [Present-day Greenland](http://websrv.cs.umt.edu/isis/index.php/Present_Day_Greenland): [Greenland_5km_v1.1.nc](http://websrv.cs.umt.edu/isis/images/a/a5/Greenland_5km_v1.1.nc)
- [Bamber et al (2013) dataset](http://www.the-cryosphere.net/7/499/2013/tc-7-499-2013.html) : Available upon request to the authors
- [Rignot and Mouginot (2012) dataset for Greenland](http://onlinelibrary.wiley.com/doi/10.1029/2012GL051634) : Available upon request to the authors
- [Morlighem et al (2013)](http://dx.doi.org/10.5067/5XKQD5Y5V3VN) : [more info here](http://sites.uci.edu/morlighem/dataproducts/mass-conservation-dataset/)
    - Note: for ease of use, the Morlighem et al dataset is currently read-in with inverted y-coordinate. You need to transform it first before reading in the program.

Install
-------

Download and install the code:

    git clone https://github.com/perrette/icedata.git
    cd icedata
    python setup.py install
    
Currently, the data mentioned above are expected to be located under `~home/icedata`. 
The structure under the `icedata` directory is currently kept as close as possible to 
the original data source. This means, no clear order... Admittedly this could be made 
simpler, and it is planned to add a search_file function to add some simplicity in how
the data is organized on disk, to impose as few constraints as possible on the user.
For now, please check in the source files what is expected...
e.g. for Bamber et al 2013, check in icedata/greenland/bamber2013.py

    NCFILE = os.path.join('greenland','bamber_2013_1km','Greenland_bedrock_topography_V3.nc')
    
Or from python, for the same dataset:

    import icedata.greenland.bamber2013
    print icedata.greenland.bamber2013.NCFILE

will return:

    greenland/bamber_2013_1km/Greenland_bedrock_topography_V3.nc
    
In case of problem with your own data organization, just edit the source code of each dataset to indicate the 
precise path of the corresponding netCDF file.

