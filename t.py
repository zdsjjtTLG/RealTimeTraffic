# -- coding: utf-8 --
# @Time    : 2024/7/21 11:36
# @Author  : TangKai
# @Team    : ZheChengData


from src.micro.path_generator import PathDemands


if __name__ == '__main__':
    ge = PathDemands(macro_link_path=r'./data/RealWorld/Scene1/LinkAfterModify.shp',
                     macro_node_path=r'./data/RealWorld/Scene1/NodeAfterModify.shp')
    ge.rnd_path()
