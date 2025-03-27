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
import os

############### Insert your own parameters below #########################
# set working directory - everything will be relative to this directory
path = r''
arcpy.env.workspace = path

# shapefile
shapefile = 'some_polygon.shp'
# check that file exists - QC
print(arcpy.Exists(shapefile))
# Create a feature layer from the shapefile
arcpy.management.MakeFeatureLayer(shapefile)

# point to las file or directory if files
inLas = r''
# name for lasdata set to be made - you choose
lasdata = ''
# Now load our digital elevation model 
dem_p = r''
dem = arcpy.Raster(dem_p)

# make lasdataset object
arcpy.management.CreateLasDataset(inLas, lasdata)

# Extract LAS points within shapefile boundary - big speed boost
arcpy.ddd.ExtractLas(lasdata, path, shapefile, boundary = shapefile,
                    out_las_dataset = 'clipped_lasdata.lasd')

clipped_lasdata = 'clipped_lasdata.lasd'
# output parameters
out_p = r''
date = r''

#################################################################
# Processing and Quality Control steps
# 1. Classify LAS noise on the clipped dataset
arcpy.ddd.ClassifyLasNoise(clipped_lasdata, method='RELATIVE_HEIGHT', edit_las='CLASSIFY',
                           ground=dem, low_z=-0.25, high_z=5)

# 2. classify ground 
arcpy.ddd.ClassifyLasGround(clipped_lasdata)

# 3. select only the points that are not noise and not ground,
canopy_las = arcpy.management.MakeLasDatasetLayer(
    clipped_lasdata, "QC_filter", class_code=[1])


############################################################
######## Stop and Inspect Raster for abnormalities #########
############################################################

# Calculate plot ht based on diff between dem and canopy_las
# Convert LAS to raster based on elevation
arcpy.conversion.LasDatasetToRaster(in_las_dataset = canopy_las, 
                                    out_raster = 'CellHeightsAuto.tif',
                                    value_field = 'ELEVATION',
                                    sampling_type = 'CELLSIZE',
                                    sampling_value = 0.25)

# make variable
cellht = arcpy.Raster('CellHeightsAuto.tif')

# raster algebra to subtract Cellheights from DEM to produce plants heights
plantht = cellht - dem

# Zonal stats to summarize results on within shapefile polygons
arcpy.sa.ZonalStatisticsAsTable(in_zone_data = shapefile,
                               zone_field = 'id',
                               in_value_raster = plantht,
                               percentile_values = [5, 25, 90, 99],
                               out_table = 'AutoHeights.dbf')

# path to save csv results
out_csv = os.path.join(date, 'AutoHt.csv')
arcpy.TableToTable_conversion('AutoHeights.dbf', out_p, out_csv)