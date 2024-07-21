# -- coding: utf-8 --
# @Time    : 2024/7/21 11:09
# @Author  : TangKai
# @Team    : ZheChengData

from __future__ import absolute_import
from __future__ import print_function


import os
import sys
import time
import traci  # noqa
import pickle
import sumolib  # noqa
import datetime
import optparse
import numpy as np
import pandas as pd
import geopandas as gpd
from ..log import LogRecord
from datetime import timedelta
from sumolib import checkBinary  # noqa
from shapely.geometry import Point
from ..GlobalField import GlobalField, GpsField


field = GlobalField()
gps_field = GpsField()

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


MAX_WAIT_TIME = field.MAX_WAIT_TIME


class MicroSim(object):
    def __init__(self, save_log: bool = False, out_fldr: str = r'./', loc_frequency: float = 5.0,
                 offset: tuple[float, float] = None, crs: str = None, time_format: str = "%Y-%m-%d %H:%M:%S",
                 start_year: int = 2022, start_month: int = 5, start_day: int = 15, start_hour: int = 10,
                 start_minute: int = 20, start_second: int = 12):
        """

        :param save_log:
        :param out_fldr:
        :param loc_frequency:
        :param offset:
        :param crs:
        :param time_format:
        :param start_year:
        :param start_month:
        :param start_day:
        :param start_hour:
        :param start_minute:
        :param start_second:
        """
        self.save_log = save_log
        self.log_fldr = out_fldr
        self.loc_frequency = loc_frequency
        self.offset = offset
        self.crs = crs
        self.log_machine = LogRecord(out_fldr=out_fldr, file_name=r'SumoCar.log', save_log=save_log)
        self.time_format = time_format
        self.start_year = start_year
        self.start_month = start_month
        self.start_day = start_day
        self.start_hour = start_hour
        self.start_minute = start_minute
        self.start_second = start_second
        self.start_time = datetime.datetime(year=start_year, month=start_month, day=start_day,
                                            hour=start_hour, minute=start_minute, second=start_second)
        self.gps_data_fldr = os.path.join(out_fldr, 'gps')
        if not os.path.exists(self.gps_data_fldr):
            os.makedirs(self.gps_data_fldr)

    def run(self, file_name_array=None, lock=None):
        """
        :param file_name_array: 与DTA进程的共享数组, 初始值为1000个元素的array, 值全为-1, DTA进程可以修改其中的值, mirco进程只读不写
        修改和读取都需要获取锁, DTA进程第i( i>= 0)次输出一个新的轨迹文件后, 将该数组的第i个元素修改为i
        :param lock: 变量锁对象
        :return:
        """
        step = 0
        _step = 0
        # 开始TraCI微观仿真迭代循环
        agent_loc = list()
        time_step = 1.0
        while traci.simulation.getMinExpectedNumber() > 0:
            s = time.time()
            traci.simulationStep()
            step += 1
            _step += 1
            sim_time = self.start_time + timedelta(seconds=time_step * step)
            car_id_list = traci.vehicle.getIDList()
            agent_loc.extend(
                [agent, np.array(traci.vehicle.getPosition(agent)), sim_time, traci.vehicle.getSpeed(agent)] for agent in
                list(car_id_list))
            self.log_machine.out_log(rf'No.{step} steps, SimTime: {sim_time}')

            if _step * time_step >= self.loc_frequency:
                _step = 0
                loc_df = pd.DataFrame(agent_loc, columns=[gps_field.AGENT_ID_FIELD, 'loc', gps_field.TIME_FIELD,
                                                          gps_field.SPEED_FIELD])
                loc_df[gps_field.LNG_FIELD] = loc_df['loc'].apply(lambda x: x[0]) - self.offset[0]
                loc_df[gps_field.LAT_FIELD] = loc_df['loc'].apply(lambda x: x[1]) - self.offset[1]
                del loc_df['loc']
                gps_num = len(loc_df)
                self.log_machine.out_log(rf'###### Push gps, {gps_num} pieces of data')
                with open(os.path.join(self.gps_data_fldr, rf'{step}-gps'), 'wb') as f:
                    pickle.dump(loc_df, f)
                agent_loc = list()

            used_time = time.time() - s
            if _step == 0:
                self.log_machine.out_log(rf'cost {used_time} secs...')
            if used_time < time_step:
                time.sleep(time_step - used_time)

        traci.close()
        sys.stdout.flush()


