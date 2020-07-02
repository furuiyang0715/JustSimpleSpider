import datetime
import os
import re
import sys

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from ExchangeMargin.base import MarginBase


class BoardCast(MarginBase):
    """公告播报"""
    def __init__(self):
        super(BoardCast, self).__init__()
        # 展示这个时间点之后的公告
        self.offset = 10
        self.early_day = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min) - datetime.timedelta(days=self.offset)
        self.table = 'margin_announcement'

    def show_info(self, market):
        """选择爬虫库的原始资讯数据"""
        self._spider_init()
        sql = """
        select time, content from {} where market = {} and time >= '{}'; 
        """.format(self.table, market, self.early_day)
        board_info = self.spider_client.select_all(sql)
        return board_info

    def show_sql_info(self, secu_code):
        """
        查看 datacenter 数据库的情况
        """
        self._dc_init()
        format_str = "聚源内部编码: {} 列出时间: {}, 移除时间: {} 当前是否在清单内: {}\n"
        inner_code = self.get_inner_code(secu_code)
        sql = """
        select * from {} where InnerCode = {};  
        """.format(self.target_table_name, inner_code)
        ret = self.dc_client.select_all(sql)
        # 将其转化为 str 语句
        msg1 = '融资:'
        msg2 = '融券:'
        for r in ret:
            if r.get("TargetCategory") == 10:
                msg1 += format_str.format(r.get("InnerCode"), r.get("InDate"), r.get("OutDate"), r.get("TargetFlag"))
            else:
                msg2 += format_str.format(r.get("InnerCode"), r.get("InDate"), r.get("OutDate"), r.get("TargetFlag"))
        return msg1 + msg2

    def start(self):
        # sh
        msg = "*** 公告播报[最近{}天] *** \n".format(self.offset) + '*'*20 + '上交所' + "*"*20 + '\n'
        infos = self.show_info(83)
        for info in infos:
            _time = info.get("time")
            content = info.get("content")
            msg += "发布时间: {} 公告内容: {}\n".format(_time, content)
            secu_codes = re.findall(r"\d{6}", content)
            msg += '公告中包含的证券代码有 {}\n'.format(secu_codes)
            if secu_codes:
                for secu_code in secu_codes:
                    msg += "{}: \n".format(secu_code)
                    sql_info = self.show_sql_info(secu_code)
                    msg += sql_info
                    msg += '\n'
            msg += "*"*20 + '\n'

        # sz
        msg += '*'*20 + '深交所' + "*"*20 + '\n'
        infos = self.show_info(90)
        for info in infos:
            _time = info.get("time")
            content = info.get("content")
            msg += "发布时间: {} 公告内容: {}\n".format(_time, content)
            secu_codes = re.findall(r"\d{6}", content)
            msg += '公告中包含的证券代码有 {}\n'.format(secu_codes)
            if secu_codes:
                for secu_code in secu_codes:
                    msg += "{}: \n".format(secu_code)
                    sql_info = self.show_sql_info(secu_code)
                    msg += sql_info
                    msg += '\n'
            msg += "*"*20 + '\n'

        print(msg)

        self.ding(msg)


def board_task():
    BoardCast().start()


if __name__ == "__main__":
    board_task()
