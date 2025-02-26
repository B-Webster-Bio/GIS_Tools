# GIS_Tools
Scripts and tools written in Arcpy to process and extract remote sensing data in the ArcGIS program. Note the general philosophy of these scripts is to calculate raw statistics from rasters and export data out as soon as possible because working with Arcpy in ArcGIS is prohibitive. Would probably be best to transition workflows to a more open source platform. 

* FlightlineMosiac.py - Help process hyperspectral mosiacs into flightlines
* MSThrehAndExtract.py - Create a canopy filter based on SAVI values for 5 band multispectral data. Extract plot based reflectance from filtered rasters.
* LAS_HeightExtract.py - Extract plot heights from point cloud data using a ground elevation model and raster algebra.
* WorkNotebooks - Jupyter notebooks for Remote Sensing for N project presented at NAPPN 2024 and MGC 2024.
