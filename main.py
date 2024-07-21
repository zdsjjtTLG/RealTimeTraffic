# -- coding: utf-8 --
# @Time    : 2024/7/21 11:12
# @Author  : TangKai
# @Team    : ZheChengData
import os

import traci  # noqa
import pickle
import sumolib  # noqa
import pandas as pd
from time import sleep
from sumolib import checkBinary  # noqa
from src.micro.micro_simulation import MicroSim
from src.GlobalField import GlobalField
from multiprocessing import Process, Lock, Array
from src.SumoConvert import SumoConvert


field = GlobalField()


# def main():
#     """
#     联仿主函数
#     :return:
#     """
#
#     # 标记文件序列的共享数组, 1000容量
#     counter_array = Array('i', [-1] * 1000)
#     mutex = Lock()
#     process_list = []
#     process_list.append(Process(target=false_dta, args=(mutex, counter_array)))
#     process_list.append(Process(target=real_world, args=(mutex, counter_array)))
#
#     for p in process_list:
#         p.start()
#     for p in process_list:
#         p.join()
#
#     # counter_array = Array('i', [-1] * 1000)
#     # mutex = Lock()
#     # process_list = []
#     # false_dta(mutex, counter_array)


class RealTimeCondition(object):
    def __init__(self, scene_fldr: str = 'Scene1', save_log=True, loc_frequency=5.0, out_fldr: str = r'./'):
        self.scene_fldr = scene_fldr
        self.out_fldr = out_fldr
        self.save_log = save_log
        self.loc_frequency = loc_frequency

    def get_net_info(self) -> tuple[float, float, str]:
        x_offset, y_offset, crs = None, None, None
        for file in os.listdir(self.scene_fldr):
            if file.endswith('.net.xml'):
                x_offset, y_offset, crs = SumoConvert.get_prj_info(net_path=os.path.join(self.scene_fldr, file))
                break
        if x_offset is None:
            raise ValueError('do not find .net.xml files')
        return x_offset, y_offset, crs

    def start_sim(self, lock: Lock = None, file_name_array=None):
        """
        sumo仿真进程
        :param lock:
        :param file_name_array:
        :return:
        """
        x_offset, y_offset, crs = self.get_net_info()
        print(x_offset)
        # sumoBinary = checkBinary('sumo')
        sumoBinary = checkBinary('sumo-gui')
        assert os.path.exists(os.path.join(self.scene_fldr, "sumo.sumocfg"))
        traci.start([sumoBinary, "-c", os.path.join(self.scene_fldr, "sumo.sumocfg"),
                     "--tripinfo-output", os.path.join(self.out_fldr, "trip_info.xml")])

        sim = MicroSim(out_fldr=self.out_fldr,
                       save_log=self.save_log, loc_frequency=self.loc_frequency, offset=(x_offset, y_offset),
                       crs=crs)
        sim.run(file_name_array=file_name_array, lock=lock)


def match():
    with open(r'./data/output/Scene1/gps/25-gps', 'rb') as f:
        df = pickle.load(f)
    print(df)
    from shapely.geometry import Point
    import geopandas as gpd
    df['geometry'] = df[['lng', 'lat']].apply(lambda x: Point(x), axis=1)
    df = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:32649')
    df = df.to_crs('EPSG:4326')
    df.to_file(r'gps.geojson', driver='GeoJSON')
if __name__ == '__main__':
    # main()
    # rtc = RealTimeCondition(loc_frequency=5.0, save_log=True,
    #                         scene_fldr=r'./data/input/Scene1', out_fldr=r'./data/output/Scene1')
    # rtc.start_sim()

    match()