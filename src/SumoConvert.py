# -- coding: utf-8 --
# @Time    : 2024/2/10 15:27
# @Author  : TangKai
# @Team    : ZheChengData


import pyproj
import xml.etree.cElementTree as ET

"""从net.xml中读取坐标系信息"""


class SumoConvert(object):
    def __init__(self):
        pass

    @staticmethod
    def get_prj_info(net_path: str = None, crs: str = None, ) -> tuple[float, float, str]:
        """
        必须时平面投影
        从net.xml解析微观车道级路网
        :param net_path:
        :param crs:
        :return:
        """
        net_tree = ET.parse(net_path)

        net_root = net_tree.getroot()
        location_ele = net_root.findall('location')[0]
        try:
            prj4_str = location_ele.get('projParameter')
        except:
            prj4_str = None

        if crs is None:
            assert prj4_str is not None
            crs = 'EPSG:' + prj4_2_crs(prj4_str=prj4_str)
        try:
            x_offset, y_offset = list(map(float, location_ele.get('netOffset').split(',')))
        except:
            x_offset, y_offset = 0, 0
        return x_offset, y_offset, crs


def prj4_2_crs(prj4_str: str = None) -> str:
    crs = pyproj.CRS(prj4_str)
    x = crs.to_epsg()
    return str(x)


if __name__ == '__main__':
    pass
