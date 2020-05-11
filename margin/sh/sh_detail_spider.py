import datetime
import json
import logging
import os
import pprint
import sys
import time
import urllib
from urllib.request import urlretrieve
import requests
import xlrd

sys.path.append('./../../')
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
        self.detail_table_name = 'margin_sh_detail_spider'

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
        dirname, filename = os.path.split(os.path.abspath(__file__))
        file = os.path.join(dirname, "data_dir/{}.xls".format(dt))
        try:
            urlretrieve(url, file, self.callbackfunc)
        except urllib.error.HTTPError:
            logger.warning("不存在这一天的数据{}".format(dt))
            return False
        except TimeoutError:
            logger.warning("超时 {} ".format(dt))
        except Exception as e:
            logger.warning("下载失败 : {}".format(e))
            raise Exception
        else:
            return True

    def load(self):
        dt = self.start_dt
        while dt <= self.end_dt:
            self.load_xls(dt)
            dt = dt + datetime.timedelta(days=1)

    def get_detail_dt_list(self, dt, market, category):
        """获取爬虫库中具体某一天的 detail 清单"""
        spider = self._init_pool(self.spider_cfg)

        # sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}' and SecuMarket =83 and TargetCategory = {};
        # TODO 在 sh 的 detail 中未对融资融券进行区分
        sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}' and SecuMarket =83; 
        '''.format(self.detail_table_name, dt, category)
        # print(sql_dt)
        # sys.exit(0)
        dt_ = spider.select_one(sql_dt).get("mx")
        logger.info("距离{}最近的之前的一天是{}".format(dt, dt_))
        # sql = '''select InnerCode from {} where ListDate = '{}' and SecuMarket = {} and TargetCategory = {}; '''.format(self.detail_table_name, dt_, market, category)
        sql = '''select InnerCode from {} where ListDate = '{}' and SecuMarket = {}; '''.format(self.detail_table_name, dt_, market)
        ret = spider.select_all(sql)
        ret = [r.get("InnerCode") for r in ret]
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
          `TargetCategory` int(11) DEFAULT NULL COMMENT '标的类别',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `un2` (`SecuMarket`, `TargetCategory`,`ListDate`, `InnerCode`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='融资融券标的证券历史清单';
        '''.format(self.detail_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()
        logger.info('建表成功 ')

    def read_xls(self, dt):
        dt = dt.strftime("%Y%m%d")
        dirname, _ = os.path.split(os.path.abspath(__file__))
        file = os.path.join(dirname, "data_dir/{}.xls".format(dt))
        wb = xlrd.open_workbook(file)
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
        fields = ["SecuMarket", "InnerCode", 'SecuCode', 'SecuAbbr', 'SerialNumber', 'ListDate', 'TargetCategory', ]
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
            item['TargetCategory'] = 10
            # print(data)
            # print(item)
            client = self._init_pool(self.spider_cfg)
            self._save(client, item, self.detail_table_name, fields)
            items.append(item)
            try:
                client.dispose()
            except:
                logger.warning("dispose error")

    def get_dt_list(self):
        # # 确定一个需要下载的时间点 或者 时间点列表
        # start_dt = datetime.datetime(2020, 1, 2)
        # dt_list = [start_dt, ]

        # 根据起止时间生成列表
        dt_list = []
        start_dt = datetime.datetime(2020, 3, 1)
        end_dt = datetime.datetime(2020, 4, 2)
        # end_dt = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        dt = start_dt
        while dt <= end_dt:
            dt_list.append(dt)
            dt += datetime.timedelta(days=1)

        return dt_list

    def start(self):
        # 建表
        self._create_table()

        # 下载所需的 detail 数据
        dt_list = self.get_dt_list()
        # print(dt_list[0])
        # print(dt_list[-1])
        # print(len(dt_list))

        for dt in dt_list:
            logger.info("开始下载 {} 的数据".format(dt))
            ret = self.load_xls(dt)
            if ret:
                logger.info('开始将 {} 的数据入库 '.format(dt))
                self.read_xls(dt)

            print()
            print()

        lst1 = self.get_detail_dt_list(datetime.datetime(2020, 5, 11), 83, 10)
        print(lst1)


if __name__ == "__main__":
    now = lambda: time.time()
    start_dt = now()
    DetailSpider().start()
    # DetailSpider()._start()
    logger.info("耗时 {} 秒".format(now() - start_dt))
