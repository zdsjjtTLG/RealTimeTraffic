# -- coding: utf-8 --
# @Time    : 2024/7/21 11:12
# @Author  : TangKai
# @Team    : ZheChengData


class GlobalField(object):
    def __init__(self):
        self.AGENT_ID = 'agent_id'
        self.DEPART_TIME = 'departure_time_in_secs'
        self.EDGE_SEQUENCE = 'edge_sequence'
        self.MAX_WAIT_TIME = 450 # secs

class GpsField(object):
    """gps数据字段"""
    def __init__(self):
        self.POINT_SEQ_FIELD = 'seq'
        self.LOC_TYPE = 'loc_type'
        self.SUB_SEQ_FIELD = 'sub_seq'
        self.ORIGIN_POINT_SEQ_FIELD = '__ori_seq'
        self.TIME_FIELD = 'time'
        self.LNG_FIELD = 'lng'
        self.LAT_FIELD = 'lat'
        self.HEADING_FIELD = 'heading'
        self.AGENT_ID_FIELD = 'agent_id'
        self.PRE_AGENT_ID_FIELD = 'pre_agent'
        self.ORIGIN_AGENT_ID_FIELD = 'origin_agent_id'
        self.TYPE_FIELD = 'type'
        self.NEXT_LINK_FIELD = 'next_link'
        self.GEOMETRY_FIELD = 'geometry'
        self.FROM_GPS_SEQ = 'from_seq'
        self.TO_GPS_SEQ = 'to_seq'
        self.SPEED_FIELD = 'speed'

        self.GROUP_FIELD = 'group'
        self.SUB_GROUP_FIELD = 'sub_group'
        self.NEXT_P = 'next_p'
        self.PRE_P = 'pre_p'
        self.NEXT_SEQ = 'next_seq'
        self.NEXT_TIME = 'next_time'
        self.PRE_TIME = 'pre_time'
        self.ADJ_TIME_GAP = 'time_gap'
        self.ADJ_DIS = 'gps_adj_dis'
        self.ADJ_X_DIS = 'gps_adj_xl'
        self.ADJ_Y_DIS = 'gps_adj_yl'
        self.ADJ_SPEED = 'adj_speed'

        self.DENSE_GEO = '__dens_geo__'
        self.N_SEGMENTS = '__n__'

        self.X_DIFF = 'gv_dx'
        self.Y_DIFF = 'gv_dy'
        self.VEC_LEN = 'gvl'

        self.PLAIN_X = 'prj_x'
        self.PLAIN_Y = 'prj_y'

        self.PRE_PLAIN_X = 'pre_prj_x'
        self.PRE_PLAIN_Y = 'pre_prj_y'
