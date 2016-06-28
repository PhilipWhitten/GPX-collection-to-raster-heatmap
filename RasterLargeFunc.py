import os
import gdal
import ogr    

def RasterizeLarge(name, layer, extent, pixel_size):
    """Used to rasterize a layer where the raster extent is much larger than the layer extent
    Arguments:
    name       -- (string) filename without extension of raster to be produced
    layer      -- (vector layer object) vector layer containing the data to be rasterized (tested with point data)
    extent     -- (list: x_min, x_max, y_min, y_max) extent of raster to be produced
    pixel_size -- (list: x_pixel_size, y_pixel_size) 1 or 2 pixel different pixel sizes may be sent
    """
    
    if isinstance(pixel_size, (list, tuple)):
        x_pixel_size = pixel_size[0]
        y_pixel_size = pixel_size[1]

    else:
        x_pixel_size = y_pixel_size = pixel_size

    x_min, x_max, y_min, y_max = extent    
    # determines the x and y resolution of the file (lg = large)
    x_res_lg = int((x_max - x_min) / x_pixel_size)+2
    y_res_lg = int((y_max - y_min) / y_pixel_size)+2

    if x_res_lg > 1 and y_res_lg > 1:
        pass
    else:
        print ('Your pixel size is larger than the extent in one dimension or more')
        return

    x_min_sm, x_max_sm, y_min_sm, y_max_sm = layer.GetExtent()

    if x_min_sm >= x_min and x_max_sm <= x_max and y_min_sm >= y_min and y_max_sm <= y_max:
        pass
    else:
        print ('The extent of the layer is in one or more parts outside of the extent provided')
        print (extent)
        print (layer.GetExtent())
        return

    nx = int((x_min_sm - x_min)/x_pixel_size) #(number of pixels between main raster origin and minor raster)
    ny = int((y_max - y_max_sm)/y_pixel_size)
    
    x_res_sm = int((x_max_sm - x_min_sm) / x_pixel_size)+2
    y_res_sm = int((y_max_sm - y_min_sm) / y_pixel_size)+2

    #determines upper left corner of small layer raster
    x_min_sm = x_min + nx * x_pixel_size
    y_max_sm = y_max - ny * y_pixel_size

    #______Creates a temporary raster file for the small raster__________
    try:
        # create the target raster file with 1 band
        sm_ds = gdal.GetDriverByName('GTiff').Create('tempsmall.tif', x_res_sm, y_res_sm, 1, gdal.GDT_Byte)
        sm_ds.SetGeoTransform((x_min_sm, x_pixel_size, 0, y_max_sm, 0, -y_pixel_size))
        sm_ds.SetProjection(layer.GetSpatialRef().ExportToWkt())
        gdal.RasterizeLayer(sm_ds, [1], layer, burn_values=[1])
       
        sm_ds.FlushCache()
        #______Gets data from the new raster in the form of an array________
        in_band = sm_ds.GetRasterBand(1)
        in_band.SetNoDataValue(0)
        sm_data = in_band.ReadAsArray()
    finally:
        sm_ds = None  #flushes data from memory.  Without this you often get an empty raster.

    #_____Creates an output file with the provided name and extent that contains the small raster.
    name = name + '.tif'

    try:
        lg_ds = gdal.GetDriverByName('GTiff').Create(name, x_res_lg, y_res_lg, 1, gdal.GDT_Byte)

        if lg_ds is None:
            print 'Could not create tif'
            return
        else:
            pass

        lg_ds.SetProjection(layer.GetSpatialRef().ExportToWkt())
        lg_ds.SetGeoTransform((x_min, x_pixel_size, 0.0, y_max, 0.0, -y_pixel_size))
        lg_band = lg_ds.GetRasterBand(1)
        lg_data = in_band.ReadAsArray()

        lg_band.WriteArray(sm_data, xoff = nx, yoff = ny)
        lg_band.SetNoDataValue(0)
        lg_band.FlushCache()
        lg_band.ComputeStatistics(False)
        lg_band = None

    finally:
        del lg_ds, lg_band, in_band
        os.remove('tempsmall.tif')
    return
