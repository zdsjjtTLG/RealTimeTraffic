# -- coding: utf-8 --
# @Time    : 2024/7/21 11:12
# @Author  : TangKai
# @Team    : ZheChengData


import traci  # noqa
import pickle
import sumolib  # noqa
import pandas as pd
from time import sleep
from sumolib import checkBinary  # noqa
from src.micro_simulation import run, get_options
from src.GlobalField import GlobalField
from multiprocessing import Process, Value, Lock, Array


field = GlobalField()


def main():
    """
    联仿主函数
    :return:
    """

    # 标记文件序列的共享数组, 1000容量
    counter_array = Array('i', [-1] * 1000)
    mutex = Lock()
    process_list = []
    process_list.append(Process(target=false_dta, args=(mutex, counter_array)))
    process_list.append(Process(target=real_sumo, args=(mutex, counter_array)))

    for p in process_list:
        p.start()
    for p in process_list:
        p.join()

    # counter_array = Array('i', [-1] * 1000)
    # mutex = Lock()
    # process_list = []
    # false_dta(mutex, counter_array)


def false_dta(lock, file_name_array):
    """
    DTA生产进程
    :param lock:
    :param file_name_array:
    :return:
    """
    # 每生产出15min, 900s的数据就存一次文件
    export_time_gap = 900

    # 总共生产15个文件
    n = 4

    # 用于记录输出次数
    export_count = 0

    # 每次生产数据的时间开销, secs
    cost_time = 2

    # agent_id不能有重复
    # 按照出发时间(secs)升序排列
    df = pd.read_csv(r'./Meso_output/scenario_jh_motorway/meso_trj.csv')

    # 归0
    df[field.DEPART_TIME] = df[field.DEPART_TIME] - df[field.DEPART_TIME].min()
    df.sort_values(by=field.DEPART_TIME, ascending=True, inplace=True)
    print(df[field.DEPART_TIME])

    for i in range(0, n):
        # print(rf'第{export_count}次第{i} secs 生产数据...')
        _df = df[(df[field.DEPART_TIME] < (i + 1) * export_time_gap) &
                 (df[field.DEPART_TIME] >= i * export_time_gap)].copy()
        _df.reset_index(inplace=True, drop=True)

        print(rf'第{i}次数据生产中......')
        sleep(cost_time)
        print(rf'第{i}次生产成功......')

        print(_df[[field.AGENT_ID, field.DEPART_TIME, field.EDGE_SEQUENCE]])
        get_lock = True
        while get_lock:
            if lock.acquire(timeout=3.5):
                print(rf'生产进程拿到变量锁....')
                # 存储文件
                with open(rf'./Meso_output/{export_count}-data.df', 'wb') as f:
                    pickle.dump(_df, f)
                file_name_array[export_count] = export_count

                get_lock = False
                print(rf'写文件{export_count}-data.df成功!, 锁释放...')
                print(list(file_name_array))
                # 更新
                export_count += 1
                lock.release()
            else:
                print(rf'生产进程获取锁失败...., 继续尝试获取...')


def real_sumo(lock, file_name_array):
    """
    sumo仿真进程
    :param lock:
    :param file_name_array:
    :return:
    """
    # 基于微观的路段连接关系构建有向图, 用于路径搜索
    #
    # using_history_route = False
    # meso_ft_micro_edge_map_dict = init_main(re_init=True,
    #                                         prj_fldr=r'E:\work\机荷高速仿真\DATlite-SUMO')

    # sumoBinary = checkBinary('sumo')
    sumoBinary = checkBinary('sumo-gui')

    traci.start([sumoBinary, "-c", "./Micro_input/sumo.sumocfg",
                 "--tripinfo-output", "./Micro_output/tripinfo.xml"])

    run(file_name_array=file_name_array, lock=lock)


if __name__ == '__main__':
    main()