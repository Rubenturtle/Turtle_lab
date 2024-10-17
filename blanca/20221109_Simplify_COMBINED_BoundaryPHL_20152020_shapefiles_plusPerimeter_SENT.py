########################################################################################################################################
#9 November 2022 (Blanca Perez-Lapena)
#This script outputs several indicator values (as a csv file)for different simplification tolerances of a boundary shapefile.
#INPUT: 
#- boundary polygon shapefile
#- tolerances for simplification of the boundary
#- Method for simplification
#OUTPUT:
#- CSV file with values of: simplified shapefile name; tolerance used in the simplification; number of vertices in the original and simplified boundary;
#total area (2D) in km2 of the original and simplified boundary shapefile; total perimeter (2D) in km of the original and simplified boundary shapefile;
#num of vertices to total area in km2 in the the original and simplified boundary shapefile; perimeter in km to total area in km2 in the the original and simplified boundary shapefile;
#percent agreement between original and simplified boundary shapefile as:
#[(total area in m2 of the intersection of original and simplified boundary shapefile)/(total area in m2 of the union of original and simplified boundary shapefile)]*100

#Notes: runs slow (e.g. intersection and union processes take quite some time, processing within the for loop)
########################################################################################################################################

#PHL tested: Requires as input the combined polygon shapefile for a Region
import processing
import os
from qgis.core import (
    QgsVectorLayer
)
import csv
#location input combined boundary shapefile
inpath = 'D:/Blanca/Work/UNDESA_NEW/Philippines/1_Data_PHL/Boundaries_PHL/Boundaries_NAMRIA/1_Processing/From_20220912_Steph_NAMRIA/20221018_Combining_20152020_boundary_R8/'
inshpn = 'R8_Combined_Boundary_2015_2020_SP' #avoid .shp as it will taken as part of the name
inpathshpn = inpath + inshpn
outpath = 'D:/Blanca/TEMPORAL/s20221109/'
outshpn = 'R8_Simply_comb20152020_T'
simplify_meth = 0 #Method for simplification "Distance"
##create csv file to add the output variables and open it
csv_outpathn = outpath + 'csv_file.csv' #output csv name
csv_file = open(csv_outpathn, 'w') # open the file in the write mode
#create headers
out_fieldnames = ["name_simplif", "tolerance", "num_vertices_ORI","num_vertices_simpl", "totalAreakm2_ori", "totalAreakm2_simpl", \
"perimKm_ori", "perimKm_simpl", "vert_to_areakm2_ori", "vert_to_areakm2_simpl", "perimeter_to_areakm2_ori", "perimeter_to_areakm2_simpl","perc_agreement"]
writer = csv.DictWriter(csv_file, fieldnames=out_fieldnames)
writer.writeheader() #write headers
####################
##calculate the total area of the original combined boundary
v_ori_layer = QgsVectorLayer(inpathshpn + '.shp', inshpn, "ogr")
#Add combined boundary to the Layers Panel
QgsProject.instance().addMapLayer(v_ori_layer)
##calculate the total area
qStr = ("?query=SELECT SUM(st_area([" + v_ori_layer.name() + "].geometry)) AS tot_aream FROM [" + v_ori_layer.name() + "]&nogeometry")
totaream2_layer_ori=QgsVectorLayer(qStr,'totaream2_layer_ori','virtual')
feat = QgsFeature() # create empty feature in memory
totaream2_layer_ori.getFeatures().nextFeature(feat) #assign the iterator's first feature to feat
attrs = feat.attributes() #get the attributes from the first feature
total_aream2_ori=attrs[0] #store the area in variable for later use (m2)
total_areaKm2_ori = total_aream2_ori/1000000 #calculate the total area (km2)
del(totaream2_layer_ori) #delete virtual layer
##calculate the total perimeter
qStr = ("?query=SELECT SUM(st_perimeter([" + v_ori_layer.name() + "].geometry)) AS tot_perim FROM [" + v_ori_layer.name() + "]&nogeometry")
totaperim_layer_ori=QgsVectorLayer(qStr,'totaperim2_layer_ori','virtual')
feat = QgsFeature() # create empty feature in memory
totaperim_layer_ori.getFeatures().nextFeature(feat) #assign the iterator's first feature to feat
attrs = feat.attributes() #get the attributes from the first feature
total_perim_ori=attrs[0] #store the perimeter in variable for later use (m)
total_periKm_ori = total_perim_ori/1000 #calculate perimeter (km)
del(totaperim_layer_ori) #delete virtual layer
##calculate perimeter to area
perim_to_areaKm2_ori = total_periKm_ori/total_areaKm2_ori

#extract the number of vertices in the original combined boundary
mem_player_ori = processing.run("native:extractvertices", {'INPUT':v_ori_layer.name(),'OUTPUT':'memory:vert'})['OUTPUT']
#count the number of vertices and save it in variable
vertices_count_ori = mem_player_ori.featureCount()
#calculate num of vertices divided by total area of original boundary (km2) and save it to variable
vert_to_areaKm2_ori = vertices_count_ori/total_areaKm2_ori
del(mem_player_ori) #delete virtual layer
####################

#define tolerances for simplification
t_list = [0.5, 1, 1.5, 2, 2.5]
for i in t_list:
    #define the output shapefile name. The name includes the tolerance used for simplification
    outpathshpn = outpath + outshpn + str(i)
    #Simplify function using the i value in the list for the tolerance in Simplify
    processing.run("native:simplifygeometries", \
    {'INPUT':inpathshpn + '.shp', \
    'METHOD':simplify_meth,'TOLERANCE':i,'OUTPUT':outpathshpn + '.shp'})
    ##obtain the number of vertices in the simplified polygon layer; vlayer pointing to the newly created simplified layer
    vlayer = QgsVectorLayer(outpathshpn + '.shp', "" + outshpn + str(i) + "", "ogr")
    if not vlayer.isValid():
        print("Layer failed to load!")
    QgsProject.instance().addMapLayer(vlayer)
    #number of vertices
    mem_player = processing.run("native:extractvertices", {'INPUT':vlayer,'OUTPUT':'memory:vert'})['OUTPUT']
    vertices_count = mem_player.featureCount()
    #calculate area of simplified boundary
    qStr = ("?query=SELECT SUM(st_area([" + vlayer.name() + "].geometry)) AS tot_aream FROM [" + vlayer.name() + "]&nogeometry")
    totaream2_layer=QgsVectorLayer(qStr,"totaream2_layer","virtual")
    feat = QgsFeature() # create empty feature in memory
    totaream2_layer.getFeatures().nextFeature(feat) #assign the iterator's first feature to feat
    attrs = feat.attributes() #get the attributes from the first feature
    total_aream2_simpl=attrs[0] #store the area in variable for later use (m2)
    total_areaKm2_simpl = total_aream2_simpl/1000000 #area (km2)
    #vertices to area (km2) of simplified boundary
    vert_to_areaKm2_simpl = vertices_count/total_areaKm2_simpl
    del(totaream2_layer) #delete to reuse
    #calculate total perimeter
    qStr = ("?query=SELECT SUM(st_perimeter([" + vlayer.name() + "].geometry)) AS tot_perim FROM [" + vlayer.name() + "]&nogeometry")
    totaream2_layer=QgsVectorLayer(qStr,'totaperim2_layer_simpl','virtual')
    feat = QgsFeature() # create empty feature in memory
    totaream2_layer.getFeatures().nextFeature(feat) #assign the iterator's first feature to feat
    attrs = feat.attributes() #get the attributes from the first feature
    total_perim_simpl=attrs[0] #store the perimeter in variable for later use (m)
    total_periKm_simpl = total_perim_simpl/1000 #perimeter (km)
    del(totaream2_layer) #delete virtual layer
    #perimeter (km) to area (km2)
    perim_to_areaKm2_simpl = total_periKm_simpl/total_areaKm2_simpl
    #add spatial indexes
    processing.run("native:createspatialindex", {'INPUT': v_ori_layer})
    processing.run("native:createspatialindex", {'INPUT': vlayer})
    #intersection of original and simplified layers
    mem_intlayer = processing.run("native:intersection", {'INPUT':v_ori_layer,'OVERLAY':vlayer,'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'','OUTPUT':'memory:inters'})['OUTPUT']
    QgsProject.instance().addMapLayer(mem_intlayer)
    #calculate total area of the intersection
    qStr = ("?query=SELECT SUM(st_area([" + mem_intlayer.name() + "].geometry)) AS tot_aream FROM [" + mem_intlayer.name() + "]&nogeometry")
    totaream2_layer=QgsVectorLayer(qStr,"totaream2_layer","virtual")
    feat = QgsFeature() # create empty feature in memory
    totaream2_layer.getFeatures().nextFeature(feat) #assign the iterator first feature to feat
    attrs = feat.attributes() #get the attributes from the first feature
    total_aream2_int=attrs[0] #store the area in variable for later use (m2)
    total_areaKm2_int = total_aream2_int/1000000 #area (km2)
    #union of original and simplified layers
    mem_unlayer = processing.run("native:union", {'INPUT':v_ori_layer,'OVERLAY':vlayer,'OVERLAY_FIELDS_PREFIX':'','OUTPUT':'memory:munion'})['OUTPUT']
    QgsProject.instance().addMapLayer(mem_unlayer)
    del(totaream2_layer)#delete to reuse
    qStr = ("?query=SELECT SUM(st_area([" + mem_unlayer.name() + "].geometry)) AS tot_aream FROM [" + mem_unlayer.name() + "]&nogeometry")
    totaream2_layer=QgsVectorLayer(qStr,"totaream2_layer","virtual")
    feat = QgsFeature() # create empty feature in memory
    totaream2_layer.getFeatures().nextFeature(feat) #assign the iterator's first feature to feat
    attrs = feat.attributes() #get the attributes from the first feature
    total_aream2_un=attrs[0] #store the area in variable for later use (m2)
    total_areaKm2_un = total_aream2_un/1000000 #area (km2)
    #percent agreement
    perc_agreement = (total_aream2_int/total_aream2_un)*100
    #write values to csv file
    writer.writerow({"name_simplif":outpathshpn,"tolerance":i,"num_vertices_ORI":vertices_count_ori,"num_vertices_simpl":vertices_count,\
    "totalAreakm2_ori":total_areaKm2_ori,"totalAreakm2_simpl":total_areaKm2_simpl,\
    "perimKm_ori":total_periKm_ori, "perimKm_simpl":total_periKm_simpl,\
    "vert_to_areakm2_ori":vert_to_areaKm2_ori,"vert_to_areakm2_simpl":vert_to_areaKm2_simpl,"perimeter_to_areakm2_ori":perim_to_areaKm2_ori, "perimeter_to_areakm2_simpl":perim_to_areaKm2_simpl, "perc_agreement":perc_agreement})
    QgsProject.instance().removeMapLayer(mem_intlayer.id())
    QgsProject.instance().removeMapLayer(mem_unlayer.id())
    QgsProject.instance().removeMapLayer(vlayer.id())
    del(mem_player)
    del(totaream2_layer)
    output_csv = []

csv_file.close()