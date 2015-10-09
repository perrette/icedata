# icedata
python repository to read ice data from various sources and return it in a standardized way


Datasets
--------
Not provided here ! You need to get it yourself...

- [Present-day Greenland](http://websrv.cs.umt.edu/isis/index.php/Present_Day_Greenland): [Greenland_5km_v1.1.nc](http://websrv.cs.umt.edu/isis/images/a/a5/Greenland_5km_v1.1.nc)
- [Bamber et al (2013) dataset](http://www.the-cryosphere.net/7/499/2013/tc-7-499-2013.html) : Available upon request to the authors
- [Rignot and Mouginot (2012) dataset for Greenland](http://onlinelibrary.wiley.com/doi/10.1029/2012GL051634) : Available upon request to the authors
- [Morlighem et al (2013)](http://dx.doi.org/10.5067/5XKQD5Y5V3VN) : [more info here](http://sites.uci.edu/morlighem/dataproducts/mass-conservation-dataset/)
    - Note: for ease of use, the Morlighem et al dataset is currently read-in with inverted y-coordinate. You need to transform it first before reading in the program.


Dependencies
------------
- numpy [1.9.2]
- [netCDF4](https://github.com/Unidata/netcdf4-python) [1.1.7] - [see instructions here](https://github.com/perrette/python-install/blob/master/README.md#netcdf4)
- [dimarray (dev)](https://github.com/perrette/dimarray) [0.1.9.dev-852f76e]: please install the latest version from github. The pip version will not work 
