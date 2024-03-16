# Imports
import arcpy
import pandas as pd
import os

"""Workflow in arcpy to threshold a MultiSpectral image by SAVI and then extract spectral data from 
    thresholded images. Visual inspection of data rasters with multiple indices suggests that SAVI 
    produces the most contrast between plots and background.

# Input:
    Shapefile - .dbf that defines experimental field plots
    5 Rasters from MS remote Sensing (R, G, B, NIR, RE) - .tif

# Output:
    - Multiple supplemental files (one for each band + one of filter statistics)
    - One Concatenated csv of plot level information for each band + filter stats

# Operation: arcpy is a closed source python library so the easiest way to run this script is by 
            opening a python script or notebook directly in arcgis pro and then copy paste in. 
            Insert in your own path, shapefile (.dbf), raster file names, output for csvs, and date(as string).
            Threshold parameter adjusts filtering. 0 for no filter. A value around 0.29 works for most days but not all. 
"""

############### Insert your own parameters below #########################

# Set environment/working directory - the folder with rasters 
path = r"C:\"
# Load shape file describing field plots
shapefile = r"C:\"
# Create a feature layer from the shapefile
arcpy.management.MakeFeatureLayer(shapefile)

# Text strings of the 5 individuals MS rasters
redfile = 'Thompson_Maize_06_16_2022_MS_transparent_reflectance_red.tif'
greenfile = 'Thompson_Maize_06_16_2022_MS_transparent_reflectance_green.tif'
bluefile = 'Thompson_Maize_06_16_2022_MS_transparent_reflectance_blue.tif'
nirfile = 'Thompson_Maize_06_16_2022_MS_transparent_reflectance_nir.tif'
rededgefile = 'Thompson_Maize_06_16_2022_MS_transparent_reflectance_red edge.tif'

# Directory to save csv files to
dir_for_csvs = r"C:"
date = '20220616_MS'
# Threshold to filter out pixels based on SAVI value, usually 0.05 - 0.35
threshold = 0.05

#########################################################################################
################### Everything below here automated #####################################
####################################################################################
arcpy.env.workspace = path
# Load as Raster Objects
redraster = arcpy.Raster(redfile)
greenraster = arcpy.Raster(greenfile)
blueraster = arcpy.Raster(bluefile)
nirraster = arcpy.Raster(nirfile)
rededgeraster = arcpy.Raster(rededgefile)
rasters = [redraster, greenraster, blueraster, nirraster, rededgeraster]

# Composite MS rasters into 1
arcpy.management.CompositeBands(rasters, 'Composite5Band.tif')

# Calculated SAVI with the NIRband(#4) and Red band(#1) 
SAVI_raster = arcpy.ia.SAVI("Composite5Band.tif", 4, 1, 0.5)

# Create mask to threshold with, early in season it needs to be very relaxed limit
SAVI_mask = (SAVI_raster > threshold)
# Set all values that did not pass threshold to NA, important destinction from 0 I learned
SAVI35extract = arcpy.sa.ExtractByAttributes(SAVI_mask, 'VALUE = 1')

# Use raster map algebra to apply mask to each band
red_filtered = redraster * SAVI35extract
green_filtered = greenraster * SAVI35extract
blue_filtered = blueraster * SAVI35extract
nir_filtered = nirraster * SAVI35extract
rededge_filtered = rededgeraster * SAVI35extract

# variables for zonal extract
inZone = shapefile
zoneField = 'id'
MSList = ['Red', 'Green', 'Blue', 'NIR', 'RedEdge']
# Create empty list to store csv files for later
csvs = []

# For each band extract reflectance per zone(polygon) convert to csv
for i in range(5):
    InRast = rasters[i]
    OutTab_dbf = MSList[i] + 'Table.dbf'
    OutTab_csv = MSList[i] + 'Table.csv'
    csvs.append(OutTab_csv)
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
csvs.append('SAVIMASKTable.csv')

os.chdir(dir_for_csvs)

# Loop, add column ID and concat
data_frames = []
for c in csvs:
    df = pd.read_csv(c)
    df['Source'] = date + '_' + c[:-9]
    data_frames.append(df)

Concat_df = pd.concat(data_frames, ignore_index=True)

# make df_mask look like df_reflectance
Concat_df.drop(columns = ['VARIETY', 'MAJORITY', 'MINORITY'], inplace=True)

out_concat = date + 'Concat.csv'
Concat_df.to_csv(out_concat, index = False)
