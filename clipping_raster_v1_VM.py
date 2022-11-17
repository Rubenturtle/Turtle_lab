"""This is a way to clip the data but If I were you I would go to the jupyter notebook one"""
import os
import sys
from osgeo import gdal

gdal.UseExceptions()

#Set the size of the file with gdalinfo or QGIS
width = 158159
height = 79080
#Set the size of the tile
tilesize = 64000

os.chdir(r"//akif.internal/public/z_resources/hydrosoil/hihydrosoil_ruben") #works fine

for i in range(0, width, tilesize): #tilesize marks from where to where
    for j in range(0, height, tilesize):

        # gdaltranString = "gdal_translate -of GTIFF -co “COMPRESS=LZW” -co “PREDICTOR=2” -co “TILED=YES” -srcwin "+str(i)+", "+str(j)+", "+str(tilesize)+", " \
        #     +str(tilesize)+" isric-bdticm-M-250m-ll.tif isric-bdticm-M-250m-ll_"+str(i)+"_"+str(j)+".tif"
        gdaltranString = "gdal_translate -of GTIFF -srcwin "+str(i)+", "+str(j)+", "+str(tilesize)+", " \
            +str(tilesize)+" ksat_m_250m_subsoil_deflate_1.tif ksat_m_250m_subsoil_deflate_1_"+str(i)+"_"+str(j)+".tif"
        
        print(gdaltranString)
        os.system(gdaltranString)


    
