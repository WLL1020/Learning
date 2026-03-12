"""
计算SI指数
使用蓝光波段和近红外波段计算，还用了全部波段的平均值

"""

from osgeo import gdal
import rasterio
import numpy as np
import os


# 初始化数组
banda_data = None  # files[1] 对应第二个文件（索引从0开始）
bandb_data = None  # files[4] 对应第五个文件

# band1 = Caostal band2 = blue b3 = green b4 = red b5 = nir b6 = swir1 b7 = swir2 

# Shadow Vegetation index
def Cal_SVI(R_NIR,R_RED):
    return (R_NIR - R_RED)* R_NIR/(R_NIR + R_RED)
# NDVI
def Cal_NDVI(R_NIR,R_RED):
    return (R_NIR - R_RED)/(R_NIR + R_RED)

# Shadow index
def Cal_SI(in_path):
    """
    输入文件地址，数据为7个波段内数据
    """
    files = [f for f in os.listdir(in_path) if f.endswith('.tif') or f.endswith('.TIF')]
    files.sort()  # 确保文件顺序一致
        
    # 初始化数组
    b_blue = None  # files[1] 对应第二个文件（索引从0开始）
    b_nir = None  # files[4] 对应第五个文件

    # band1 = Caostal band2 = blue b3 = green b4 = red b5 = nir b6 = swir1 b7 = swir2 
    # 读取需要的波段数据
    for i, file in enumerate(files):
        if i == 1:  # 第二个文件
            file_path = os.path.join(in_path, file)
            with rasterio.open(file_path) as src:
                b_blue = src.read(1).astype(np.float32)
        elif i == 4:  # 第五个文件
            file_path = os.path.join(in_path, file)
            with rasterio.open(file_path) as src:
                b_nir = src.read(1).astype(np.float32)
    # 确保数据读取成功
    if banda_data is None or bandb_data is None:
        raise ValueError("未能读取所需波段数据")

    # 计算所有文件的平均值（这里计算的是每个像素在所有文件中的平均值）
    # 需要读取所有文件
    all_data = []
    for file in files:
        file_path = os.path.join(in_path, file)
        with rasterio.open(file_path) as src:
            data = src.read(1).astype(np.float32)
            all_data.append(data)

    # 计算平均值
    all_data_array = np.array(all_data)   
    L_mean = np.mean(all_data_array, axis=0)

    # # 计算SI指数
    denominator = (b_blue + b_nir )*L_mean
    denominator = np.where(denominator == 0, 1e-10, denominator)  # 避免除0
    SI = (banda_data - bandb_data)/ denominator
    return SI

# Normalization the Vegetation Index
def Normalization(VI):
    """
    对指数归一化处理
    """
    return  2 * (VI - np.nanmin(VI)) / (np.nanmax(VI) - np.nanmin(VI) + 1e-10) - 1  # 归一化处理
    # SI = np.where(SI <= -1000,-1000,SI)