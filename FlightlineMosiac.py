######################## Flightline Mosiac Maker ######################
#######################################################################

# Inputs: Path to folder with raw cubes to process (dir_str)
#         Outpath folder to save flightlines (outp)
#         Number of flightlines (n_flightlines)
#         Number of Bands (SWIR or VNIR) (n_bands)

# Outputs: One mosiac flightline with statistics calulated for each flightline
# in the field

# To be ran inside of ArcGIS Pro
import arcpy
# os to handle file management
import os
# re for file name parser
import re
# sys to close program if a check fails
import sys
# datetime to print progress
from datetime import datetime

####################### User variables ################################
# Path to input with raw cubes to process , the 'r' needs to be there
dir_str = r'Whole path i.e.(r'C:\somedrive\someuser\somefolder')
# outpath to folder that will save flightlines
outp = r'Whole path'
n_flightlines = # An integer describing number of flightlines
n_bands = # An int describing number of bands in data cube
#######################################################################


# Helper functions 
# extract int to sort files sequentially
def extract_integers(s):
    numbers = re.findall(r'\d+', s)
    return [int(num) for num in numbers]

# Divide chunks to split files into flightlines
def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]       

# Process
# Sort files
wd = os.listdir(dir_str)
files = []
for fname in wd:
    if not fname.endswith('.dat') : continue
    files.append(fname)

# change our workingdir for quality of life
arcpy.env.workspace = dir_str
    
# Sort files based on the integer (I think timestamps) in file names
sorted_list = sorted(files, key = extract_integers)

# Check 1 that the number of cubes is divisible by the number of flightlines
cubes = int(len(sorted_list)/n_flightlines)
if len(files) % n_flightlines == 0: 
    print('Number of data cubes to process:', len(files))
    print('Number of cubers per flightline:', cubes)
else: 
    print('Incompatible shapes between flightlines and files, exiting')
    sys.exit()

# Divide the files into flightlines       
x = list(divide_chunks(sorted_list, cubes))

# Create a dictionary of lists for each flightline to process
flightlines_dic = {}
for i in range(len(x)):
    list_name = 'FL{}'.format(i)
    flightlines_dic[list_name] = x[i]

# Check 2 that band number matches what we might expexct from SWIR or VNIR
if n_bands == 270:
    sensor = 'SWIR_'
    print('Sensor:', sensor)
elif n_bands == 274:
    sensor = 'VNIR_'
    print('Sensor:', sensor)
else:
    print('Sensor should be either 270 or 274 bands, exiting')
    sys.exit()

# Loop through our dictionary and mosiac into flightlines then calc stats in flightline
for fl in flightlines_dic:
    outn = sensor + fl + '.img'
    print(fl)
    formatted_time = datetime.now().strftime("%D:%H:%M:%S")
    print('StartTime:', formatted_time)
    out_Dataset = arcpy.management.CreateRasterDataset(out_path = outp, out_name=outn, pixel_type='32_BIT_FLOAT', 
                                                       compression= 'LZ77',
                                                       pyramids= "PYRAMIDS -1 ", pyramid_origin = "-180 90", number_of_bands=n_bands)[0]
    out_Dataset = arcpy.Raster(out_Dataset)
    Updated_Target_Raster = arcpy.management.Mosaic(inputs = flightlines_dic[fl], target=out_Dataset, mosaic_type='FIRST', 
                                               background_value=0, nodata_value=0, mosaicking_tolerance=0.5)[0]
    print('Mosiac done, calculating statistics')
    formatted_time = datetime.now().strftime("%D:%H:%M:%S")
    print('StartTime:', formatted_time)
    file_to_stat = os.path.join(outp, outn)
    arcpy.management.CalculateStatistics(file_to_stat, x_skip_factor = 3, y_skip_factor = 3)

