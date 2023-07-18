import arcpy

"""Workflow in arcpy to threshold a MultiSpectral image by SAVI and then extract spectral data from 
    thresholded images.

# Input:
    Shapefile - .shp that defines experimental field plots
    5 Rasters from MS remote Sensing (R, G, B, NIR, RE) - .tif

# Output:
    5 csv tables of spectral data from thresholded rasters - one for each MS band 

# Operation: arcpy is a closed source python library so the easiest way to run this script is by 
            opening a python script or notebook directly in arcgis pro and then copy paste in.

"""

############### Insert your own parameters below #########################

# Set environment/working directory - the folder with rasters 
arcpy.env.workspace = r"C:\Users\bdub\Desktop\2021HIPS_Orthophotos\8_10_21\Maize_GXE_08_10_2021_MS2"

# Load shape file describing field plots
shapefile = r"C:\Users\bdub\OneDrive - Michigan State University\RemoteSensing\ShapeFiles\Projected\2021HIPS_buff_project.shp"
# Create a feature layer from the shapefile
HIPS = arcpy.management.MakeFeatureLayer(shapefile, "HIPS")

# Text strings of the 5 individuals MS rasters
redfile = 'Maize_GXE_08_10_2021_MS2_transparent_reflectance_red.tif'
greenfile = 'Maize_GXE_08_10_2021_MS2_transparent_reflectance_green.tif'
bluefile = 'Maize_GXE_08_10_2021_MS2_transparent_reflectance_blue.tif'
nirfile = 'Maize_GXE_08_10_2021_MS2_transparent_reflectance_nir.tif'
rededgefile = 'Maize_GXE_08_10_2021_MS2_transparent_reflectance_red edge.tif'

# Directory to save csv files to
dir_for_csvs = r"C:\Users\bdub\Desktop\2021HIPS_Orthophotos"

#########################################################################################
################### Everything below here automated #####################################
####################################################################################
# Load as Raster Objects
redraster = arcpy.Raster(redfile)
greenraster = arcpy.Raster(greenfile)
blueraster = arcpy.Raster(bluefile)
nirraster = arcpy.Raster(nirfile)
rededgeraster = arcpy.Raster(rededgefile)
rasters = [redraster, greenraster, blueraster, nirraster, rededgeraster]

# Composite MS rasters into 1
arcpy.management.CompositeBands(rasters, 'Composite5Band.tif')

# Load the composite you just made
Composite5Band = arcpy.Raster('Composite5Band.tif')

# Calculated SAVI with the NIRband(#4) and Red band(#1) 
SAVI_raster = arcpy.ia.SAVI("Composite5Band.tif", 4, 1, 0.5)

# Create mask to threshold with
SAVI_mask = (SAVI_raster > 0.35)
SAVI_mask.save('SAVI35mask.tif')

# Set all values that did not pass threshold to NA, important destinction from 0 I learned
SAVI35extract = arcpy.sa.ExtractByAttributes(SAVI_mask, 'VALUE = 1')

# Use raster map algebra to apply mask
red_filtered = redraster * SAVI35extract
green_filtered = greenraster * SAVI35extract
blue_filtered = blueraster * SAVI35extract
nir_filtered = nirraster * SAVI35extract
rededge_filtered = rededgeraster * SAVI35extract

# variables for zonal extract
inZone = shapefile
zoneField = 'id'
MSList = ['Red', 'Green', 'Blue', 'NIR', 'RedEdge']

# For each band extract reflectance per zone(polygon) convert to csv
for i in range(5):
    InRast = rasters[i]
    OutTab_dbf = MSList[i] + 'Table.dbf'
    OutTab_csv = MSList[i] + 'Table.csv'
    arcpy.sa.ZonalStatisticsAsTable(in_zone_data=inZone,
                                   zone_field=zoneField,
                                   in_value_raster=InRast,
                                   out_table = OutTab_dbf)
    arcpy.TableToTable_conversion(OutTab_dbf, dir_for_csvs, OutTab_csv)

# Calculate the number of cells that pass SAVI filter
arcpy.sa.ZonalStatisticsAsTable(in_zone_data=shapefile,
                                   zone_field=zoneField,
                                   in_value_raster=SAVI_mask,
                                   out_table = 'SAVIMASKTable.dbf')
arcpy.TableToTable_conversion('SAVIMASKTable.dbf', dir_for_csvs, 'SAVIMASKTable.csv')

# Will have to merge and organize these two sets of tables after. Struggled to alter zonal stat types for some reason.
