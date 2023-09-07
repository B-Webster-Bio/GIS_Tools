FlightlineMosiac.py - Script written to automatically parse hyperspectral cubes of either VNIR or SWIR 
into flightlines, mosiac the flightlines, and then calculate statistics for flightline mosiac. 
FlightMosiac.py can only parse flightlines if the number of cubes per flightline is the same
	(e.g. 9 flightlines with 5 cubes each exactly). 
It produces one ".img" file for each flightline titled like "SWIR_FL0.img" where FL0 is flightline 0.

Running script: copy and paste FlightMosiac.py into the notebook section of ArcGISPro. Replace the following
variables with the ones for your project. 

 * dir_str - path to folder with all the cubes to be processed.
 * outp - outpath to folder to save flightline mosiac
 * n_flightlines = a number describing how many flightlines
 * n_bands = a number describing how many bands in data cubes also informs sensor used

It can take multiple days to run a full field. To keep track of progress a time stamps is printed at the start 
of each flightline mosiac and then statistics step. Alternate text output will appear if the number of cubes in 
dir_str is incompatible with n_flightlines or if n_bands does not equal 270(SWIR) or 274(VNIR). 

After the script completes and you load a flightline mosiac into ArcGISPro, it will prompt to calculate statistics. 
To the best of my knowledge, this appears to be some sort of bug because you can say "No" and still perform tasks 
that require raster statistics such as changing the display bands. 