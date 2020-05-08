import datetime
import logging
import os
import random
import sys
import time
import urllib
from urllib.request import urlretrieve

import xlrd

from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SzListSpider(MarginBase):
    def __init__(self):
        # 主页链接
        # self.web_url = 'http://www.szse.cn/disclosure/margin/object/index.html'
        # api 接口
        # self.base_api_url = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1834_xxpl&txtDate=2010-04-01&tab1PAGENO=1&random=0.483243785962155'
        # 有数据存在的起始时间
        # self.start_dt = datetime.datetime(2010, 3, 29)
        # 文件下载链接  eg. 2020-05-07 random.random
        # 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1834_xxpl&txtDate=2020-05-08&random=0.5377421243834375&TABKEY=tab1'
        self.base_file_url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1834_xxpl&txtDate={}&random={}&TABKEY=tab1'
        self.inner_code_map = self.get_inner_code_map()
        self.year = 2020
        self.start_dt = datetime.datetime(self.year, 1, 1)
        self.end_dt = datetime.datetime(self.year, 12, 31)
        self.history_table_name = 'sz_margin_history'
        # 存在历史数据的文件夹
        self.data_dir = '/Users/furuiyang/gitzip/JustSimpleSpider/margin/sz/data_dir'

    def read(self):
        """将历史数据存入数据库 """
        # years = sorted(os.listdir(self.data_dir))
        # print(years)   # ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']

        error_list = []
        for year in sorted(os.listdir(self.data_dir)):
        # for year in ['2010', '2011',]:
            print(year)
            year_dir = os.path.join(self.data_dir, year)
            for file in sorted(os.listdir(year_dir)):
                # print(file)
                dt = file.split(".")[0]
                dt = datetime.datetime.strptime(dt, "%Y-%m-%d")
                file_path = os.path.join(year_dir, file)
                print(dt, file_path)
                try:
                    self.read_xls(file_path, dt)
                except:
                    error_list.append(dt)
                print()
                print()
                print()

        print(error_list)

    def read_xls(self, file: str, dt: datetime.datetime):
        """
        读取单个时间点的文件
        :param file: 文件路径
        :param dt: 文件对应的日期
        :return:
        """
        wb = xlrd.open_workbook(file)
        detail = wb.sheet_by_name("融资融券标的证券信息")

        rows = detail.nrows - 1
        # print("总数据量 {}".format(rows))

        heads = detail.row_values(0)
        # print("表头信息", heads)
        # ['证券代码', '证券简称', '融资标的', '融券标的', '当日可融资', '当日可融券', '融券卖出价格限制']

        fields = [
            'SecuMarket',
            'SecuCode',
            'InnerCode',
            'SecuAbbr',
            'SerialNumber',
            'ListDate',
            'FinanceBool',     # 融资标的
            'FinanceBuyToday',  # 当日可融资
            'SecurityBool',   # 融券标的
            'SecuritySellToday',  # 当日可融券
            'SecuritySellLimit',  # 融券卖出价格限制
        ]

        # list_date = datetime.datetime.strptime(str(dt), "%Y%m%d")
        items = []
        for i in range(1, rows+1):
            data = detail.row_values(i)
            # print(data)
            item = dict()
            item['SecuMarket'] = 90  # 深交所
            secu_code = data[0]
            item['SecuCode'] = secu_code
            item['InnerCode'] = self.get_inner_code(secu_code)
            item['SecuAbbr'] = data[1]
            item['SerialNumber'] = i
            item['ListDate'] = dt
            item['FinanceBool'] = 1 if data[2] == "Y" else 0    # 融资标的
            item['FinanceBuyToday'] = 1 if data[4] == "Y" else 0  # 当日可融资
            item['SecurityBool'] = 1 if data[3] == 'Y' else 0  # 融券标的
            item['SecuritySellToday'] = 1 if data[5] == "Y" else 0  # 当日可融券
            item['SecuritySellLimit'] = 1 if data[6] == "Y" else 0  # 融券卖出价格限制
            items.append(item)

        client = self._init_pool(self.spider_cfg)
        for item in items:
            self._save(client, item, self.history_table_name, fields)
        try:
            client.dispose()
        except:
            logger.warning("dispose error")

    def callbackfunc(self, blocknum, blocksize, totalsize):
        """
        回调函数
        :param blocknum: 已经下载的数据块
        :param blocksize:  数据块的大小
        :param totalsize: 远程文件的大小
        :return:
        """
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        sys.stdout.write("\r%6.2f%%" % percent)
        sys.stdout.flush()

    def load_xlsx(self, dt: datetime.datetime):
        """
        下载某一天的明细文件
        :param dt: eg.20200506
        :return:
        """
        dt = dt.strftime("%Y-%m-%d")
        url = self.base_file_url.format(dt, random.random())
        # print(">>>>>>>", url)
        try:
            urlretrieve(url, "./data_dir/{}/{}.xlsx".format(self.year, dt), self.callbackfunc)
        except urllib.error.HTTPError:
            logger.warning("不存在这一天的数据{}".format(dt))
        except TimeoutError:
            logger.warning("超时 {} ".format(dt))
        except Exception as e:
            logger.warning("下载失败 : {}".format(e))
            raise Exception

    def load(self):
        """下载历史文件信息"""
        dt = self.start_dt
        while dt <= self.end_dt:
            self.load_xlsx(dt)
            dt = dt + datetime.timedelta(days=1)

    def _create_table(self):
        """建表"""

        # fields = [
        #     'SecuMarket',
        #     'SecuCode',
        #     'InnerCode',
        #     'SecuAbbr',
        #     'SerialNumber',
        #     'ListDate',
        #     'FinanceBool',     # 融资标的
        #     'FinanceBuyToday',  # 当日可融资
        #     'SecurityBool',   # 融券标的
        #     'SecuritySellToday',  # 当日可融券
        #     'SecuritySellLimit',  # 融券卖出价格限制
        # ]

        sql = '''
         CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuMarket` int(11) DEFAULT NULL COMMENT '证券市场',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',
          `SecuCode` varchar(10) DEFAULT NULL COMMENT '证券代码',
          `SecuAbbr` varchar(200) DEFAULT NULL COMMENT '证券简称',
          `SerialNumber` int(10) DEFAULT NULL COMMENT '网站清单序列号',
          `ListDate` datetime NOT NULL COMMENT '列入时间',
          `FinanceBool` int NOT NULL COMMENT '融资标的 1是0否',
          `FinanceBuyToday` int NOT NULL COMMENT '当日可融资 1是0否',
          `SecurityBool` int NOT NULL COMMENT '融券标的 1是0否',
          `SecuritySellToday` int NOT NULL COMMENT '当日可融券 1是0否',
          `SecuritySellLimit` int NOT NULL COMMENT '融券卖出价格限制 1是0否',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `un2` (`ListDate`, `InnerCode`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='深交所融资融券标的证券历史清单';
        '''.format(self.history_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()

    def start(self):
        self._create_table()

        # self.load()

        self.read()


if __name__ == "__main__":
    now = lambda: time.time()
    start_dt = now()
    SzListSpider().start()
    logger.info("耗时: {}".format(now() - start_dt))
