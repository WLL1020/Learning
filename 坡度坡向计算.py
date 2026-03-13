from osgeo import gdal
import matplotlib.pyplot as plt

# 打开 DEM 文件
dem_file = r"F:\毕设数据\毕设数据_准备\陕西眉县\自定义1\自定义DEM.tif"
output_slope = r"F:\毕设数据\毕设数据_准备\陕西眉县\自定义1\自定义slope.tif"
output_aspect = "F:\毕设数据\毕设数据_准备\陕西眉县\自定义1\自定义aspect.tif"
dem = gdal.Open(dem_file)

# 计算坡度
gdal.DEMProcessing(output_slope, dem, "slope", computeEdges=True)
# 计算坡向
gdal.DEMProcessing(output_aspect, dem, "aspect", computeEdges=True)

print("ending!")