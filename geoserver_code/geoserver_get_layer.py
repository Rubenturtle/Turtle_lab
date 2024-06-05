"""We are going to get a layer from geoserver"""
# info source: https://pypi.org/project/geoserver-rest/

import os
from geo.Geoserver import Geoserver

#Initialize the library
geo = Geoserver('https://integratedmodelling.org/dev-geoserver/web/', username='', password='')


layer = geo.get_layer(layer_name='modis_MCD64A1_burned_area_2001')
print()
#path to our data direction
path=r"C:/Users/ruben.crespo/Documents/03_tests/burned_area"
