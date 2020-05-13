import json
import re
import sys
import time
from urllib.parse import urlencode

import requests


class SHReport(object):

    def __init__(self):
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

    def get_params(self):
        _timestamp = int(time.time()*1000)
        data = {
            'callback': 'jQuery1124010159023820477953_1589359759776',
            'select': 'code,name,open,high,low,last,prev_close,chg_rate,volume,amount,tradephase,change,amp_rate,cpxxsubtype,cpxxprodusta',
            'order': '',
            'begin': 0,
            'end': 25,
            "_": _timestamp,    # 当前的一个时间戳
        }
        param = urlencode(data)
        # print(param)
        return param

    def start(self):
        url = self.url+self.get_params()
        # print(url)
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            ret = resp.text
            ret = re.findall("jQuery\d{22}_\d{13}\((.*)\)", ret)[0]
            py_datas = json.loads(ret)
            _date = py_datas.get("date")
            _time = py_datas.get("time")
            _total = py_datas.get("total")
            _list = py_datas.get("list")
            # code,name,open,high,low,last,prev_close,chg_rate,volume,amount,tradephase,
            # change,amp_rate,cpxxsubtype,cpxxprodusta
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
                 item['TradePhase'],   # 振幅 tradephase
                 item['Change'],       # 涨跌 change
                 item['AmpRate'],      # 振幅 amp_rate
                 item['CPXXSubType'],
                 item['CPXXProdusta']
                 ) = one
                print(item)
                # {'SecuCode': '600000',
                # 'SecuAbbr': '浦发银行',
                # 'Open': 10.31,
                # 'High': 10.39,
                # 'Low': 10.28,
                # 'Last': 10.38,
                # 'PrevClose': 10.34,
                # 'ChgRate': 0.39,
                # 'Volume': 15574310,
                # 'Amount': 160783648,
                # 'TradePhase': 'E110',
                # 'Change': 0.04,
                # 'AmpRate': 1.06,
                # 'CPXXSubType': 'ASH',
                # 'CPXXProdusta': '   D  F             '}
                sys.exit(0)


if __name__ == "__main__":
    # SHReport().get_params()

    SHReport().start()
