import datetime

from base import SpiderBase
from configs import LOCAL


class ClsBase(SpiderBase):
    """财联社-基类"""
    def __init__(self):
        super(ClsBase, self).__init__()
        self.local = LOCAL

    def convert_dt(self, time_stamp):
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d
