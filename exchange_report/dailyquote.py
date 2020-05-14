import datetime
import json
import re
import sys
import time
from urllib.parse import urlencode

import requests

sys.path.append('./../')
from exchange_report.base import ReportBase, logger


class SHReport(ReportBase):
    """上交所行情"""
    def __init__(self):
        super(SHReport, self).__init__()
        self.url = 'http://yunhq.sse.com.cn:32041//v1/sh1/list/exchange/equity?'
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'yfx_c_g_u_id_10000042=_ck20020212032112531630665331275; seecookie=%u5149%u4E91%u79D1%u6280%2C%u5149%u4E91%u79D1%u6280%20%u878D%u8D44%u878D%u5238%2C%u878D%u8D44%u878D%u5238%2C688466; VISITED_MENU=%5B%228307%22%2C%228451%22%2C%228312%22%2C%228814%22%2C%228815%22%2C%229807%22%2C%229808%22%2C%228817%22%2C%228431%22%2C%228619%22%2C%228454%22%5D; yfx_f_l_v_t_10000042=f_t_1580616201243__r_t_1589359605854__v_t_1589359759134__r_c_18',
            'Host': 'yunhq.sse.com.cn:32041',
            'Pragma': 'no-cache',
            'Referer': 'http://www.sse.com.cn/market/price/report/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        }
        self.sub_type_map = {
            "ASH": "主板A股",
            "BSH": "主板B股",
            "KSH": "科创板",
        }
        self.table_name = 'exchange_dailyquote'
        self.fields = ['SecuCode', 'InnerCode', 'SecuAbbr', 'TradingDay', 'Open', 'High', 'Low',
                       'Last', 'PrevClose', 'ChgRate', 'Volume', 'Amount', 'RiseFall', 'AmpRate', 'CPXXSubType']

    def get_params(self, begin):
        _timestamp = int(time.time()*1000)
        data = {
            'callback': 'jQuery1124010159023820477953_1589359759776',
            'select': 'code,name,open,high,low,last,prev_close,chg_rate,volume,amount,tradephase,change,amp_rate,cpxxsubtype,cpxxprodusta',
            'order': '',
            'begin': begin,
            'end': begin + 25,
            "_": _timestamp,    # 当前的一个时间戳
        }
        param = urlencode(data)
        return param

    def _create_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuCode` varchar(10) DEFAULT NULL COMMENT '证券代码',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码', 
          `SecuAbbr` varchar(100) DEFAULT NULL COMMENT '证券简称',
          `TradingDay` datetime NOT NULL COMMENT '交易日',
          `Open` decimal(10,4) DEFAULT NULL COMMENT '今开盘(元)',
          `High` decimal(10,4) DEFAULT NULL COMMENT '最高价(元)',
          `Low` decimal(10,4) DEFAULT NULL COMMENT '最低价(元)',
          `Last` decimal(10,4) DEFAULT NULL COMMENT '最新价(元)',
          `PrevClose` decimal(10,4) DEFAULT NULL COMMENT '前收价(元)',
          `ChgRate` decimal(10,4) DEFAULT NULL COMMENT '涨跌幅(%)',
          `Volume` decimal(20,0) DEFAULT NULL COMMENT '成交量(股)',
          `Amount` decimal(19,4) DEFAULT NULL COMMENT '成交金额(元)',
          `RiseFall` decimal(10,4) DEFAULT NULL COMMENT '涨跌',
          `AmpRate` decimal(10,4) DEFAULT NULL COMMENT '振幅',
          `CPXXSubType` varchar(20) DEFAULT NULL COMMENT '版块类型',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
           UNIQUE KEY `IX_QT_DailyQuote` (`InnerCode`,`TradingDay`),
           UNIQUE KEY `PK_QT_DailyQuote` (`ID`),
           KEY `IX_QT_DailyQuote_TradingDay` (`TradingDay`)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='交易所行情';
        '''.format(self.table_name)
        client = self._init_pool(self.spider_cfg)
        client.insert(sql)
        client.dispose()

    def start(self):
        self._create_table()
        begin = 0
        while True:
            url = self.url+self.get_params(begin)
            logger.info(url)
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                ret = resp.text
                ret = re.findall("jQuery\d{22}_\d{13}\((.*)\)", ret)[0]
                py_datas = json.loads(ret)
                _date = py_datas.get("date")
                _time = py_datas.get("time")
                trade_day = datetime.datetime.strptime(str(_date), "%Y%m%d")

                _total = py_datas.get("total")
                _list = py_datas.get("list")
                # code,name,open,high,low,last,prev_close,chg_rate,volume,amount,tradephase,
                # change,amp_rate,cpxxsubtype,cpxxprodusta
                if not _list:
                    # 没有数据的时候 _list 的结果为空
                    break

                client = self._init_pool(self.spider_cfg)
                for one in _list:
                    item = dict()
                    (item['SecuCode'],     # 证券代码 code
                     item['SecuAbbr'],     # 证券简称 name
                     item['Open'],         # 开盘 open
                     item['High'],         # 最高 high
                     item['Low'],          # 最低 low
                     item['Last'],         # 最新 last
                     item['PrevClose'],    # 前收 prev_close
                     item['ChgRate'],      # 涨跌幅 chg_rate(%)
                     item['Volume'],       # 成交量(股) volume, 网页上显示的是 手, 1 手等于 100 股
                     item['Amount'],       # 成交额(元) amount， 网页上是万元
                     item['TradePhase'],   # tradephase
                     item['RiseFall'],      # 涨跌 change --> FIX change 是 mysql 关键字
                     item['AmpRate'],      # 振幅 amp_rate
                     item['CPXXSubType'],
                     item['CPXXProdusta']
                     ) = one

                    # 将类型版块进行转换
                    item['CPXXSubType'] = self.sub_type_map.get(item['CPXXSubType'])
                    # TODO 获取聚源让内部编码这一步会拖慢速度
                    inner_code = self.get_inner_code(item['SecuCode'])
                    if not inner_code:
                        raise Exception("No InnerCode.")
                    item['InnerCode'] = inner_code
                    item['TradingDay'] = str(trade_day)

                    # 去掉不需要的字段
                    item.pop('CPXXProdusta')
                    item.pop('TradePhase')
                    # print(item)
                    self._save(client, item, self.table_name, self.fields)

                client.dispose()
            else:
                raise
            begin += 25  # 每页获取 25 个


if __name__ == "__main__":

    SHReport().start()
