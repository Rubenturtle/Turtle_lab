"""We are going to connect to the Geoserver and upload some data"""
# info source: https://pypi.org/project/geoserver-rest/

import os
from geo.Geoserver import Geoserver

#Initialize the library
geo = Geoserver('http://192.168.250.122:8600/geoserver', username='', password='')

# Create a workspace if necesary
#geo.create_workspace(workspace='para_borrar')

#path to our source data
path=r"C:\Users\ruben.crespo\Downloads\MIJARES_4326"


#if this does not work, try adding the path directly into the create_shp_coverage, or change the orentaton of /

def geoserver_vector_batch(geo,path):
    for file in os.listdir(path):
        location = path +"/"+ file #we create the location
        # Upload vector data to the geoserver
        # The name, is the name of the file
        geo.create_shp_datastore(path= location, store_name='massbio', workspace='massbio')
        return print("It's over, congratulations")

geoserver_vector_batch(geo,path)

