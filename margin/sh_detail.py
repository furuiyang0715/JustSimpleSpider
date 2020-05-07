import datetime
import json
import logging
import pprint
import sys
import urllib
from urllib.request import urlretrieve
import requests
import xlrd

from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DetailSpider(MarginBase):
    def __init__(self):
        # detail_web_url = 'http://www.sse.com.cn/market/othersdata/margin/detail/index.shtml?marginDate=20200420'
        self.csv_url = 'http://www.sse.com.cn/market/dealingdata/overview/margin/a/rzrqjygk{}.xls'
        self.inner_code_map = self.get_inner_code_map()
        # self.start_dt = datetime.datetime(2010, 3, 31)
        self.year = 2020
        self.start_dt = datetime.datetime(self.year, 1, 1)
        self.end_dt = datetime.datetime(self.year, 12, 31)
        self.detail_table_name = 'detailmargin'

    def get_inner_code_map(self):
        """
        获取聚源内部编码映射表
        https://dd.gildata.com/#/tableShow/27/column///
        https://dd.gildata.com/#/tableShow/718/column///
        """
        juyuan = self._init_pool(self.juyuan_cfg)
        # 8 是开放式基金
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8) and SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        ret = juyuan.select_all(sql)
        juyuan.dispose()
        info = {}
        for r in ret:
            key = r.get("SecuCode")
            value = r.get('InnerCode')
            info[key] = value
        return info

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

    def load_xls(self, dt: datetime.datetime):
        """
        下载某一天的明细文件
        :param dt: eg.20200506
        :return:
        """
        dt = dt.strftime("%Y%m%d")
        url = self.csv_url.format(dt)
        # print(">>>>>>>", url)
        try:
            urlretrieve(url, "./data_dir/{}/{}.xls".format(self.year, dt), self.callbackfunc)
        except urllib.error.HTTPError:
            logger.warning("不存在这一天的数据{}".format(dt))
        except TimeoutError:
            logger.warning("超时 {} ".format(dt))
        except Exception as e:
            logger.warning("下载失败 : {}".format(e))
            raise Exception

    def load(self):
        dt = self.start_dt
        while dt <= self.end_dt:
            self.load_xls(dt)
            dt = dt + datetime.timedelta(days=1)

    def get_inner_code(self, secu_code):
        ret = self.inner_code_map.get(secu_code)
        if not ret:
            logger.warning("{} 不存在内部编码".format(secu_code))
            raise
        return ret

    def _create_table(self):
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='融资融券标的证券历史清单';
        '''.format(self.detail_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()


    def read_xls(self, year, dt):
        wb = xlrd.open_workbook('./data_dir/{}/{}.xls'.format(year, dt))
        detail = wb.sheet_by_name("明细信息")
        # 总数据量
        rows = detail.nrows - 1
        # 表头信息
        heads = detail.row_values(0)
        # print(heads)
        # ['标的证券代码', '标的证券简称', '本日融资余额(元)', '本日融资买入额(元)', '本日融资偿还额(元)', '本日融券余量', '本日融券卖出量', '本日融券偿还量']

        # | id | SecuMarket | InnerCode | SecuCode | SecuAbbr | SerialNumber | ListDate            | TargetCategory | CREATETIMEJZ        | UPDATETIMEJZ
        # 数据
        items = []
        list_date = datetime.datetime.strptime(str(dt), "%Y%m%d")
        for i in range(1, rows+1):
            data = detail.row_values(i)
            item = dict()
            item['SecuMarket'] = 83
            secu_code = data[0]
            item['SecuCode'] = secu_code
            item['InnerCode'] = self.get_inner_code(secu_code)
            item['SecuAbbr'] = data[1]
            item['SerialNumber'] = i
            item['ListDate'] = list_date
            item['TargetCategory'] = None
            # print(data)
            print(item)
            # self._save()
            items.append(item)

    def start(self):
        self.read_xls(2020, 20200430)

        pass


if __name__ == "__main__":
    DetailSpider().start()
