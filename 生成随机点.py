import random
import numpy as np
from osgeo import gdal
import csv


# 根据值特定范围，获得当前点值的随机点经纬度坐标
def get_random_coordinates(raster_file,     # 栅格影像地址
                            output_csv,     # 输出csv地址
                            num_points=3600,    # 生成随机点数量
                            min_n=19,       # 随机点选取原则范围最小值
                            max_n=25):      # 随机点选取范围最小值
    # 打开栅格文件
    dataset = gdal.Open(raster_file)
    if dataset is None:
        raise Exception("无法打开栅格文件")

    # 获取栅格数据
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    geotransform = dataset.GetGeoTransform()

    # 获取值为1的像元位置
    rows, cols = np.where((array >= min_n) & (array <= max_n))
    if len(rows) < num_points:
        raise Exception(f"像元数量不足{num_points}个")

    # 随机选择500个像元
    indices = random.sample(range(len(rows)), num_points)
    selected_rows = rows[indices]
    selected_cols = cols[indices]

    # 转换为经纬度坐标
    coordinates = []
    for row, col in zip(selected_rows, selected_cols):
        x = geotransform[0] + col * geotransform[1] + row * geotransform[2]
        y = geotransform[3] + col * geotransform[4] + row * geotransform[5]
        coordinates.append((x, y))

    # 将经纬度坐标保存到CSV文件
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Longitude', 'Latitude'])  # 写入表头
        for idx, (lon, lat) in enumerate(coordinates):
            writer.writerow([idx + 1, lon, lat])

# 根据经纬度坐标，得到当前影像的DN值。并将其保存到新的csv文件中。
def extract_dn_from_csv(
    input_csv,      # 输入CSV路径，表头必须包含: Index, Longitude, Latitude
    tif_file,       # 遥感影像路径
    output_csv,     # 输出CSV路径
    band_index=1    # 波段索引，默认第1波段
):
    """
    根据CSV中经纬度列表，从遥感影像中提取指定波段DN值，并保存到新的CSV。
    """
    # 打开遥感影像
    dataset = gdal.Open(tif_file)
    if dataset is None:
        raise FileNotFoundError(f"无法打开影像: {tif_file}")

    # 读取仿射变换参数
    geotransform = dataset.GetGeoTransform()
    originX = geotransform[0]
    pixelWidth = geotransform[1]
    originY = geotransform[3]
    pixelHeight = geotransform[5]  # 通常为负数

    def get_dn(lon, lat):
        """根据经纬度返回DN值"""
        pixel = int((lon - originX) / pixelWidth)
        line = int((lat - originY) / pixelHeight)

        if pixel < 0 or pixel >= dataset.RasterXSize or line < 0 or line >= dataset.RasterYSize:
            return None  # 点在影像外

        band = dataset.GetRasterBand(band_index)
        dn = band.ReadAsArray(pixel, line, 1, 1)[0, 0]
        return dn

    # 读取输入CSV
    points = []
    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            index = row['Index']
            lon = float(row['Longitude'])
            lat = float(row['Latitude'])
            points.append((index, lon, lat))

    # 写入输出CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Index', 'Longitude', 'Latitude', 'DN']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, lon, lat in points:
            dn = get_dn(lon, lat)
            writer.writerow({
                'Index': index,
                'Longitude': lon,
                'Latitude': lat,
                'DN': dn
            })

    print(f"已生成带DN值的CSV文件: {output_csv}")

if __name__ == '__main__':
    # 示例用法
    raster_file = r"F:\毕设数据\书写代码过程中数据\seviot2.tif"
    output_csv =r"F:\毕设数据\书写代码过程中数据\seviot3.csv"     
    try:
        get_random_coordinates(raster_file, output_csv, 500)
        print(f"随机点已保存到 {output_csv}")
    except Exception as e:
        print(e)

    
    extract_dn_from_csv(
        input_csv=r"F:\毕设数据\书写代码过程中数据\seviot3.csv"  ,           # 原始CSV
        tif_file=r"F:\毕设数据\书写代码过程中数据\seviot2.tif",  # 遥感影像
        output_csv=r"F:\毕设数据\书写代码过程中数据\seviot5.csv",        # 输出CSV
        band_index=1                          # 选择波段
    )
    print("ending!")



