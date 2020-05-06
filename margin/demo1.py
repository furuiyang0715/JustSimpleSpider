# coding=utf8
import datetime
import json
import logging
import re
import sys

import demjson
import requests
from lxml import html

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SHMarginSpider(object):

    def __init__(self):
        self.url = 'http://www.sse.com.cn/services/tradingservice/margin/info/againstmargin/'

    def start(self):
        """
        <li><a href="#tableData_961" data-toggle="tab">融资买入标的证券一览表
        </a></li><li><a href="#tableData_962" data-toggle="tab">融券卖出标的证券一览表
        </a></li><li><a href="#tableData_960" data-toggle="tab">融资融券可充抵保证金证券一览表
        """
        resp = requests.get(self.url)
        if resp.status_code == 200:
            page = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(page)

            # 962
            datas = doc.xpath("//div[@class='table-responsive sse_table_T01 tdclickable']/table[@class='table search_']/script[@type='text/javascript']")[0].text
            table_datas = re.findall('''tableData\['tableData_962'\] = (.*);''', datas, re.DOTALL)[0]
            py_datas = demjson.decode(table_datas)
            show_date = py_datas.get("staticDate")
            show_dt = datetime.datetime.combine(datetime.datetime.strptime(show_date, "%Y-%m-%d %H:%M:%S"), datetime.time.min)
            list_datas = py_datas.get("list")
            lst_datas = []
            for data in list_datas:
                if data:
                    lst_datas.append(data)
            for data in lst_datas:
                item = dict()
                item['SerialNumber'] = data[0]   # str
                item['SecuCode'] = data[1]
                item['SecuAbbr'] = data[2]
                item['ShowDate'] = show_dt
                # 标的类别：10-融资买入标的，20-融券卖出标的
                item['TargetCategory'] = 20
                item['SecuMarket'] = 83
                print(item)

            # 961
            datas = doc.xpath("//table[@class='table search_bdzqkc search3T']/script[@type='text/javascript']")[0].text
            show_dt = datetime.datetime.strptime(re.findall("var showdate = '(.*)'", datas)[0], "%Y%m%d")
            table_datas = re.findall('''tableData\['tableData_961'\] = (.*);''', datas, re.DOTALL)[0]
            py_datas = demjson.decode(table_datas)
            list_datas = py_datas.get("list")
            lst_datas = []
            for data in list_datas:
                if data:
                    lst_datas.append(data)
            # 编号 证券代码 证券简称
            # [['1', '510050 ', '50ETF '], ['2', '510180 ', '180ETF '], ...
            for data in lst_datas:
                item = dict()
                item['SerialNumber'] = data[0]   # str
                item['SecuCode'] = data[1]
                item['SecuAbbr'] = data[2]
                item['ShowDate'] = show_dt
                # 标的类别：10-融资买入标的，20-融券卖出标的
                item['TargetCategory'] = 10
                item['SecuMarket'] = 83
                print(item)


if __name__ == "__main__":
    SHMarginSpider().start()
