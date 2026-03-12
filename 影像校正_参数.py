
# 可以使用


from osgeo import gdal
import rasterio
import numpy as np


path = r"F:\毕设数据\处理中数据\2101b5trim.tif"
save_path = r"F:\毕设数据\testing\testCalDai5"


with rasterio.open(path) as src:
    meta_img = src.meta.copy()
    image = src.read(1).astype(np.float32)

out_image = image * (2.75*10**-5) - 0.2

output_meta = meta_img.copy()
output_meta.update({
    'dtype': 'float32',
    'count': 1,
    'nodata': 0.0,
    'driver': 'GTiff'   
})

with rasterio.open(save_path,"w",**output_meta) as dsf:
    dsf.write(out_image.astype(np.float32),1)
# print(image[3441,3661])
# print(out_image[3441,3661])
print("ending!!!!!")