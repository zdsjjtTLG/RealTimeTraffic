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
import optparse
import pandas as pd
from time import sleep
from sumolib import checkBinary  # noqa
from src.GlobalField import GlobalField


field = GlobalField()


# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


MAX_WAIT_TIME = field.MAX_WAIT_TIME


def run(file_name_array=None, lock=None):
    """
    :param file_name_array: 与DTA进程的共享数组, 初始值为1000个元素的array, 值全为-1, DTA进程可以修改其中的值, mirco进程只读不写
    修改和读取都需要获取锁, DTA进程第i( i>= 0)次输出一个新的轨迹文件后, 将该数组的第i个元素修改为i
    :param lock: 变量锁对象
    :return:
    """
    all_ready_read_file = []
    new_df = pd.DataFrame([], columns=[field.AGENT_ID, field.DEPART_TIME, field.EDGE_SEQUENCE])
    step = 0
    is_init = False
    is_break = False
    is_delay = False
    ignore_continue = False
    # 开始TraCI微观仿真迭代循环
    agent_loc = []
    while traci.simulation.getMinExpectedNumber() > 0:

        # 1.初始化时必须要反复拿锁
        while not is_init:
            sleep(0.5)  # 每间隔0.5s拿一次锁
            if lock.acquire(timeout=0.5):
                # 如果可以拿到锁, 则查看当前的file_name_array是否有更新
                print(rf'sumo仿真在第{step}个时间步拿到锁, 准备初始化...............')
                new_index_list = list(set(file_name_array) - set(all_ready_read_file) - {-1})
                if not new_index_list:
                    print('初始化数据没有生产完毕...')
                else:
                    print('初始化数据未已生产完毕...')
                    for index in new_index_list:
                        print(rf'读取./Meso_output/{index}-data.df...')
                        with open(rf'./Meso_output/{index}-data.df', 'rb') as f:
                            # agent_id, departure_time_in_secs, edge_sequence
                            load_car_df = pickle.load(f)

                            new_df = pd.concat([new_df, load_car_df])
                            new_df.reset_index(inplace=True, drop=True)

                        # 更新all_ready_read_file
                        all_ready_read_file += [index]

                        is_init = True
                lock.release()
            else:
                print(rf'sumo仿真初始化失败..., 继续等待初始数据...')

        # 2.如果当前时间步无新数据, 则不消费
        print(rf'###### Micro 开始 第{step}个时间步仿真 ######')
        if new_df.empty:
            print(rf'第{step}个时间步, 没有待仿真的新数据...')
        else:
            # 添加当前时刻的车辆以及轨迹
            consume_car(now_step=step, df=new_df)
        traci.simulationStep()
        print(rf'###### Micro 结束 第{step}个时间步仿真, 当前未消费的车辆(new_df): ######')
        print(new_df[[field.AGENT_ID, field.DEPART_TIME]])

        # 3.check是否有新的仿真数据进来
        print(rf'###### Micro仿真 结束 第{step}个时间步仿真后检查是否有新数据进入 ######')
        if lock.acquire(timeout=3.5):
            # 如果可以拿到锁, 则查看当前的file_name_array
            print(rf'sumo仿真在第{step}个时间步拿到锁...')
            new_index_list = list(set(file_name_array) - set(all_ready_read_file) - {-1})
            if new_index_list:
                print(rf'当前未读的文件:{new_index_list}')
                for index in new_index_list:
                    print(rf'读取./Meso_output/{index}-data.df...')
                    with open(rf'./Meso_output/{index}-data.df', 'rb') as f:
                        # agent_id, departure_time_in_secs, edge_sequence
                        load_car_df = pickle.load(f)
                        # new_df = new_df.append(load_car_df)
                        new_df = pd.concat([new_df, load_car_df])
                        new_df.reset_index(inplace=True, drop=True)
                    # 更新all_ready_read_file
                    all_ready_read_file += [index]
            else:
                print(rf'当前没有未读文件')
            lock.release()
        else:
            print(rf'sumo仿真在第{step}个时间步没有拿到锁...')
        print(rf'当前已读文件: all_ready_read_file: {all_ready_read_file}')

        # 4.如果SUMO仿真太快, 需要等待新数据...
        if len(new_df[new_df[field.DEPART_TIME] >= (step + 1)]) == 0 and not ignore_continue:
            print(rf'###### Micro仿真 快于 Meso仿真 在第{step}个时间步仿真结束后等待 Meso仿真 生产新数据 ######')
            # 拿锁, 取新数据
            is_delay = True
            start_wait = time.time()
            while is_delay:
                if lock.acquire(timeout=3.5):
                    # 如果可以拿到锁, 则查看当前的file_name_array
                    print(rf'sumo仿真太快, 暂停步进, 等待新数据, sumo仿真在第{step}个时间步拿到锁...')
                    new_index_list = list(set(file_name_array) - set(all_ready_read_file) - {-1})
                    print(rf'当前未读的文件:{new_index_list}')

                    for index in new_index_list:
                        print(rf'读取./Meso_output/{index}-data.df...')
                        with open(rf'./Meso_output/{index}-data.df', 'rb') as f:
                            # agent_id, departure_time_in_secs, edge_sequence
                            load_car_df = pickle.load(f)
                            # new_df = new_df.append(load_car_df)
                            new_df = pd.concat([new_df, load_car_df])
                            new_df.reset_index(inplace=True, drop=True)
                        is_delay = False
                        # 更新all_ready_read_file
                        all_ready_read_file += [index]
                    lock.release()
                else:
                    print(rf'sumo仿真太快, 暂停步进, 等待新数据, sumo仿真在第{step}个时间步没有拿到锁...')

                # 如果等待时间过久, 则认为已经没有后续数据, 继续执行
                if time.time() - start_wait > MAX_WAIT_TIME:
                    ignore_continue = True
                    is_delay = False
                    print(r'不再等待...')
                print(rf'all_ready_read_file: {all_ready_read_file}')

        a = time.time()
        car_id_list = traci.vehicle.getIDList()
        print(car_id_list)
        agent_loc.extend([agent, traci.vehicle.getPosition(agent)] for agent in list(car_id_list))
        print(time.time() - a)
        print(agent_loc)
        step += 1

    traci.close()
    sys.stdout.flush()


def consume_car(df=None, now_step=None):
    """
    微观消费车辆函数
    :param df:
    :param now_step:
    :return:
    """
    # 从df中取出时间在[now_step - 0.5, now_step + 0.5]的车辆, 认为是在now_step时间点出发
    # agent_id, departure_time_in_secs, edge_sequence
    consume_df = df[(df[field.DEPART_TIME] <= now_step + 0.5) &
                    (df[field.DEPART_TIME] >= now_step - 0.5)].copy()

    if consume_df.empty:
        print(rf'第{now_step}个时间步, 仿真的新数据中没有到达进入条件...')
    else:
        # SUMO加入车辆
        print(rf'Micro: 在第{now_step}个时间步加入车辆:')
        print(consume_df[[field.AGENT_ID, field.DEPART_TIME]])
        for _, row in consume_df.iterrows():
            car_id = str(row[field.AGENT_ID])   # 当前车辆Id
            micro_edge_seq = row[field.EDGE_SEQUENCE].split(',')  # 当前车辆的轨迹edge序列

            # 加入轨迹
            traci.route.add(rf'routes_{car_id}', micro_edge_seq)
            print(rf'adding routes_{car_id}...')
            # 加入车辆
            traci.vehicle.add(car_id, depart=now_step, routeID=rf'routes_{car_id}')
            print(rf'adding car: {car_id}...')

        # 删除已经消费掉的车辆
        df.drop(index=consume_df.index, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options