# -*- coding: utf-8 -*-
# 完成 
# 应注意存放。shp文件的文件夹里，应有其对应配套的.shx文件等

import time
import os
from osgeo import gdal
import rasterio
import numpy as np
 

def clip_batch(in_path, out_path, in_shape):
    """
    :param in_path: 需要裁剪的文件夹
    :param out_path: 输出文件夹
    :param in_shape: 存放shp的地址
    :return:
    """
    # shp_files = os.listdir(in_shape)
    # # 以列表展开所有目录下的文件名
    # for shp_file in shp_files:
    # 从列表中遍历
        #  if shp_file.endswith('.shp'):
            # 判断是否为shp文件
    shp_name = in_shape
    # 定义tif文件的目录+名称
    files = os.listdir(in_path)
    # 打开需要裁剪的文件夹,将所有文件以列表的形式列出
    for file in files:
        if file[-4:] == '.TIF' and file[-9:-7]=='SR':
            # 判断文件是否为.tif结尾
            filename = os.path.join(in_path, file)
            # 确定找到的文件名
            # 得到影像时间
            in_raster = gdal.Open(filename)
            a = filename.split('_')
            b = a[3]
            out_raster = os.path.join(out_path, b+file[-8:-4]+"trim.tif")
            
            ds = gdal.Warp(out_raster, in_raster, format='GTiff',
                    cutlineDSName=shp_name,
                    cropToCutline=True,
                    cutlineWhere=None, dstNodata=0)
            ds = None
        # 关闭处理空间，释放内存

# 进行辐射校正
def Radiometric_Correction(in_path, out_path):
    """
    :param in_path: 输入文件夹（裁剪后的影像）
    :param out_path: 输出文件夹（辐射校正后的影像）
    :return:
    """
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    
    # 获取输入文件夹中的所有tif文件
    in_files = [f for f in os.listdir(in_path) if f.endswith('.tif') or f.endswith('.TIF')]
    
    for file in in_files:
        input_file = os.path.join(in_path, file)
        
        try:
            with rasterio.open(input_file) as src:
                # 读取元数据和图像数据
                meta_img = src.meta.copy()
                image = src.read(1).astype(np.float32)
                
                # 辐射校正公式
                out_image = image * (2.75 * 10 ** -5) - 0.2
                
                # 处理无效值
                out_image[image == 0] = 0.0
                
                # 更新元数据
                output_meta = meta_img.copy()
                output_meta.update({
                    'dtype': 'float32',
                    'count': 1,
                    'nodata': 0.0,
                    'driver': 'GTiff'
                })
                
                # 生成输出文件名
                # 使用原始文件名添加后缀
                output_filename = os.path.join(out_path, file.replace('.tif', '_RC.tif').replace('.TIF', '_RC.tif'))
                
                
                # 保存辐射校正后的影像
                with rasterio.open(output_filename, "w", **output_meta) as dst:
                    dst.write(out_image.astype(np.float32), 1)
                
                print(f"{file} 辐射校正完成！保存为: {os.path.basename(output_filename)}")
                
        except Exception as e:
            print(f"处理文件 {file} 时出错: {e}")
            continue
# 删除第一步产生的裁剪文件
def remove_file(in_path):
    rm_files = os.listdir(in_path)
    for files in rm_files:
        if files[-8:]=='trim.tif':
            filename = os.path.join(in_path,files)
            if os.path.isfile(filename):
                os.remove(filename)
                print(f'删除文件{filename}')

if __name__ == "__main__":
    # 直接执行函数
    start = time.perf_counter()  # 开始时间
    in_shape = r"F:\毕设数据\毕设数据_准备\行政边界\武夷山市.shp" # 矢量范围
    in_path = r"F:\毕设数据\毕设数据_准备\LC08_L2SP_120041_20191116_20200825_02_T1"# 输入栅格路径
    out_path = r"F:\毕设数据\武夷山"  # 输出栅格路径
    clip_batch(in_path, out_path, in_shape)
    # Radiometric_Correction(out_path,out_path)
    # remove_file(out_path)
    end = time.perf_counter()  # 结束时间
    print('finish')
    print('Running time: %s Seconds' % (end - start))
    # 展示程序运行时间