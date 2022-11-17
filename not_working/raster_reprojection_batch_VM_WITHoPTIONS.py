"""This script goes for every tif file in a folder"""

import os
from sys import path
from osgeo import gdal

"""BEWARE WITH THE INDEXATION"""
path=r"//akif.internal/public/z_resources/nca_southafrica/nlc_sa_crs9221/nlc_reprojected"
out=r"//akif.internal/public/z_resources/nca_southafrica/nlc_sa_crs9221/nlc_reprojected/out_sa"


""" Set Specific options: """

""" resampleAlg == gdalconst.GRIORA_Bilinear:     new_options += ['-rb'] """

print(path)
print(os.listdir(path))
#This iterates for every file in the directory
for file in os.listdir(path):
    #we only take the ones ended with tif
    if file.endswith('.tif'):
        #we concatenate the path
        fn = path +"/"+ file
        #here is the GDAL transformation, we set the path + / + variable
        #take a look at the additional options
        # gdal.Warp(out + '/' + file, fn , resampleAlg == gdalconst.GRIORA_Bilinear ,  dstSRS = "EPSG:4326")
        
    else:
        pass
print("It's over")