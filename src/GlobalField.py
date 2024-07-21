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