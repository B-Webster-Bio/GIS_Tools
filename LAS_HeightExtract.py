import arcpy

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

############### Insert your own parameters below #########################

arcpy.env.workspace = r'C:\Users\bdub\Desktop\RemoteSensingData\2020HIPS_Orthophotos\8_18_2020'
shapefile = r"C:\Users\bdub\OneDrive - Michigan State University\RemoteSensing\ShapeFiles\Projected\2020HIPS_ShapeFinal.dbf"
# Create a feature layer from the shapefile
arcpy.management.MakeFeatureLayer(shapefile)
# point to las file(s)
inLas = r'C:\Users\bdub\Desktop\RemoteSensingData\2020HIPS_Orthophotos\8_18_2020'
# name for lasdata set to be made
lasdata = 'HIPS2020.lasd'
# Now load our digital elevation model 
dem_p = r'C:\Users\bdub\Desktop\RemoteSensingData\2020HIPS_Orthophotos\GroundModel\PointCloudDEM.tif'
dem = arcpy.Raster(dem_p)

#########################################################################################
################### Everything below here automated #####################################
####################################################################################

# load las
arcpy.management.CreateLasDataset(inLas, lasdata)
# classify ground to keep out of calculation
arcpy.ddd.ClassifyLasGround(lasdata)
# After classifying ground everything else should still be unclassified so we can filter out ground points
# 1 - unclassified
# 2 - ground, and so on
canopy_las = arcpy.management.MakeLasDatasetLayer(lasdata, "ground_filter", class_code=[1])
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
                               out_table = 'AutoHeights.dbf')
