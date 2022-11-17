"""We are going to upload some raster files to geoserver"""
# info source: https://pypi.org/project/geoserver-rest/

import os
from sys import path
from geo.Geoserver import Geoserver

#Initialize the library
geo = Geoserver('http://192.168.250.122:8600/geoserver', username='admin', password='password')

# Create a workspace
geo.create_workspace(workspace='earth_data')

# Upload raster data to the geoserver

#path to our source data
#path=r"//akif.internal/public/z_resources/nca_southafrica/nlc_sa_crs9221/nlc_reprojected/out_sa"
path=r"//akif.internal/public/demo-geo-stack/geoserver/data/earth_data"


def geoserver_raster_batch(geo,path):
    for file in os.listdir(path):
        location = path +"/"+ file #we create the location
        name = file.replace('.tif','') #store the name without .tif
        # Upload raster data to the geoserver
        geo.create_coveragestore(lyr_name=name, path=location, workspace='earth_data')
        print("imported layer")
    return print("It's over, congratulations")

geoserver_raster_batch(geo,path)


