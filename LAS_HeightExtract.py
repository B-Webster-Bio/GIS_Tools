"""Script in arcpy to generate mean, median, 90th percentile heights from point cloud data.

# Input:
    Shapefile - .dbf that defines experimental field plots
    LAS file - point cloud file from natural color or lidar 
    Ground elevation model raster - a .tif file that maps the elevation of the field.

# Output:
    - Autoheights table with mean, median, 90th percentile and other stats by plot

# Operation: arcpy is a closed source python library so the easiest way to run this script is by 
            opening a python script or notebook directly in arcgis pro and then copy paste in. 
            Insert in your own parameters. 
"""

import arcpy
############### Insert your own parameters below #########################
arcpy.env.workspace = r'C:\'
shapefile = r'C:\'
# Create a feature layer from the shapefile
arcpy.management.MakeFeatureLayer(shapefile)
# point to las file(s)
inLas = r'C:\'
# name for lasdata set to be made
lasdata = 'NAME_YEAR.lasd'
# Now load our digital elevation model 
dem_p = r'C:'
dem = arcpy.Raster(dem_p)

# load las - look at file and see if there are any noise before continuing
arcpy.management.CreateLasDataset(inLas, lasdata)
#Classify noise and look at data before continuing, can add a high_z param to help filter
arcpy.ddd.ClassifyLasNoise(lasdata, method = 'RELATIVE_HEIGHT', withheld = 'WITHHELD', ground = dem, low_z = '0 feet')

#########################################################################################
################### Everything below here automated #####################################
####################################################################################

# classify ground to keep out of calculation
arcpy.ddd.ClassifyLasGround(lasdata)
# After classifying ground everything else should still be unclassified so we can filter out ground points
# 1 - unclassified
# 2 - ground
# 7 Noise
canopy_las = arcpy.management.MakeLasDatasetLayer(lasdata, "QC_filter", class_code=[1])
arcpy.management.MakeLasDatasetLayer(canopy_las)

# Conver LAS to raster based on elevation
arcpy.conversion.LasDatasetToRaster(in_las_dataset = canopy_las, 
                                    out_raster = 'CellHeightsAuto.tif',
                                    value_field = 'ELEVATION',
                                    sampling_type = 'CELLSIZE',
                                    sampling_value = 0.25)


cellht = arcpy.Raster('CellHeightsAuto.tif')

# raster algebra to subtract Cellheights from DEM to produce plants heights
plantht = cellht - dem

arcpy.sa.ZonalStatisticsAsTable(in_zone_data = shapefile,
                               zone_field = 'id',
                               in_value_raster = plantht,
                               percentile_values = [5, 25, 90, 99],
                               out_table = 'AutoHeights.dbf')
