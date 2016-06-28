# This code creates a raster from a shapefile.
# Every feature in the shapefile is included in the raster.
# V2 successfully rasterizes every gpx file, however, the extent of each file is different.
# V3 attempts to use gdal.Rasterize instead of gdal.RasterizeLayer

import os
import gdal
import ogr    
import sys
import math
import shutil
import RasterLargeFunc
reload(RasterLargeFunc)

os.chdir(r'C:\Users\pipi\Documents\Rogaine\Tarlo\gpx')  #folder containing gpx files
pixel_size = 30 #units are in m if gpx file is left in wgs84


# open all gpx files in a folder
files = os.listdir(os.curdir)
files_copy = files
n = 0
for file in files:
    if file[-3:] == 'gpx':
        # opens a single gpx file
        try:
            ds = ogr.GetDriverByName('GPX').Open(file, 0)  #by stating driver, the code does not have to find it.
            #0 means read only mode, 1 would allow editing
            if ds is None:
                sys.exit('Could not open {0}.'.format(file))
            lyr = ds.GetLayer('track_points')  #get's the layer containing tarck points
            x_min, x_max, y_min, y_max = lyr.GetExtent()
            if n == 0:
                x_min1 = x_min
                x_max1 = x_max
                y_min1 = y_min
                y_max1 = y_max
            else:   
                if x_min < x_min1:
                    x_min1 = x_min
                if x_max > x_max1:
                    x_max1 = x_max
                if y_min < y_min1:
                    y_min1 = y_min
                if y_max > y_max1:
                    y_max1 = y_max

        finally:
            del ds, lyr
        n+=1    
extent = [x_min1, x_max1, y_min1, y_max1]

# determines the x and y resolution of the raster file
pixel_sizey = pixel_size/(111.2*math.pow(10,3))  #determines an approximate x and y size because of geographic coordinates.
pixel_sizex = pixel_size/(math.cos(((y_max1 + y_min1)/2)*(math.pi/180))*111.2*math.pow(10,3))
pixel_size = [pixel_sizex, pixel_sizey]

    #______Open's the data source and reads the extent________
   
for file in files_copy:
    if file[-3:] == 'gpx':
        # opens a single gpx file
        try:
            layer_ds = ogr.GetDriverByName('GPX').Open(file, 0) #0 means read only# Check to see if shapefile is found.

            if layer_ds is None:
                print 'Could not open %s' % (vector_fn)
                sys.exit()
                
            else:
                try:
                    layer = layer_ds.GetLayer('tracks')  #returns the first layer in the data source
                    name = file[:-4]
                    print (name)
                    RasterLargeFunc.RasterizeLarge(name, layer, extent, pixel_size)
                              
                finally:
                    layer = None

        finally:
            layer_ds = None
    else:
        pass

files = os.listdir(os.curdir)
n = 0


for file in files:
    if file[-3:] == 'tif':
        
        if n == 0:
            print (file)
            shutil.copy2(file, 'sumofgpx.tif')
            sum_ds = gdal.Open('sumofgpx.tif', 1)
            sum_band = sum_ds.GetRasterBand(1)
            sum_data = sum_band.ReadAsArray()
            n += 1
        else:        
            try:
                tif_ds = gdal.Open(file, 0)  #by stating driver, the code does not have to find it.
                if tif_ds is None:
                    sys.exit('Could not open {0}.'.format(file))
                    
                tif_band = tif_ds.GetRasterBand(1)
                tif_data = tif_band.ReadAsArray()
                sum_data = sum_data + tif_data
                print (file)

            finally:
                del tif_ds
    else:
        pass

sum_band.WriteArray(sum_data)
sum_band.SetNoDataValue(0)
sum_band.FlushCache()
sum_band.ComputeStatistics(False)
sum_band = None

del sum_ds
