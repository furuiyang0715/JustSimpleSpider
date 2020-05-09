# coding=utf8
import datetime
import logging
import re
import sys

import demjson
import requests
from lxml import html

sys.path.append("./../")
from margin.base import MarginBase
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SHMarginSpider(MarginBase):
    def _drop_table(self):
        """临时删除数据库"""
        sql = '''drop table {}; '''.format(self.spider_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()

    def _create_table(self):
        """创建爬虫数据库"""
        # fields = ['SecuMarket', 'InnerCode', 'SecuCode', 'SecuAbbr', 'SerialNumber', 'ListDate', 'TargetCategory']
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuMarket` int(11) DEFAULT NULL COMMENT '证券市场',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',
          `SecuCode` varchar(10) DEFAULT NULL COMMENT '证券代码',
          `SecuAbbr` varchar(200) DEFAULT NULL COMMENT '证券简称',
          `SerialNumber` int(10) DEFAULT NULL COMMENT '网站清单序列号',
          `ListDate` datetime NOT NULL COMMENT '列入时间',
          `TargetCategory` int(11) NOT NULL COMMENT '标的类别',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `un2` (`SecuMarket`, `TargetCategory`,`ListDate`, `InnerCode`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='融资融券标的证券清单';
        '''.format(self.spider_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()

    def __init__(self):
        self.url = 'http://www.sse.com.cn/services/tradingservice/margin/info/againstmargin/'
        self.spider_table_name = 'sh_margin_history'
        self.inner_code_map = self.get_inner_code_map()

    def start(self):
        """
        <li><a href="#tableData_961" data-toggle="tab">融资买入标的证券一览表
        </a></li><li><a href="#tableData_962" data-toggle="tab">融券卖出标的证券一览表
        </a></li><li><a href="#tableData_960" data-toggle="tab">融资融券可充抵保证金证券一览表
        """
        # self._drop_table()
        self._create_table()
        resp = requests.get(self.url)
        if resp.status_code == 200:
            page = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(page)

            fields = ['SecuMarket', 'InnerCode', 'SecuCode', 'SecuAbbr', 'SerialNumber', 'ListDate', 'TargetCategory']
            spider = self._init_pool(self.spider_cfg)

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
                item['SerialNumber'] = int(data[0])    # str
                item['SecuAbbr'] = data[2]
                item['ListDate'] = show_dt
                # 标的类别：10-融资买入标的，20-融券卖出标的
                item['TargetCategory'] = 20
                item['SecuMarket'] = 83
                secu_code = data[1].strip()
                item['SecuCode'] = secu_code
                inner_code = self.get_inner_code(secu_code)
                item['InnerCode'] = inner_code
                self._save(spider, item, self.spider_table_name, fields)

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
                item['SerialNumber'] = int(data[0])
                item['SecuAbbr'] = data[2]
                item['ListDate'] = show_dt
                # 标的类别：10-融资买入标的，20-融券卖出标的
                item['TargetCategory'] = 10
                item['SecuMarket'] = 83
                secu_code = data[1].strip()
                item['SecuCode'] = secu_code
                inner_code = self.get_inner_code(secu_code)
                item['InnerCode'] = inner_code
                self._save(spider, item, self.spider_table_name, fields)

            # 关闭数据库连接
            try:
                spider.dispose()
            except:
                pass


if __name__ == "__main__":
    SHMarginSpider().start()
