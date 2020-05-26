import datetime
import os
import random
import sys
import time
import urllib
from urllib.request import urlretrieve

import xlrd

sys.path.append("./../")
from exchange_report.base import ReportBase, logger


class SZReport(ReportBase):
    """深交所行情爬虫"""
    def __init__(self):
        super(SZReport, self).__init__()
        self.fields = ['TradingDay', 'SecuCode', 'InnerCode', 'SecuAbbr', 'PrevClose', 'Close',
                       'RiseFall', 'Amount', 'PERatio']
        self.table_name = 'szse_dailyquote'
        self.base_url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1815_stock&TABKEY=tab1&txtBeginDate={}&txtEndDate={}&radioClass=00%2C20%2C30&txtSite=all&random={}'
        self._today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        self.check_day = self._today - datetime.timedelta(days=1)

    def _create_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuCode` varchar(10) DEFAULT NULL COMMENT '证券代码',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',  
          `SecuAbbr` varchar(100) DEFAULT NULL COMMENT '证券简称',
          `TradingDay` datetime NOT NULL COMMENT '交易日',
          `PrevClose` decimal(10,4) DEFAULT NULL COMMENT '前收价(元)',
          `Close` decimal(10,4) DEFAULT NULL COMMENT '今收(元)',
          `Amount` decimal(19,4) DEFAULT NULL COMMENT '成交金额(元)',
          `RiseFall` decimal(10,4) DEFAULT NULL COMMENT '涨跌',
          `PERatio` decimal(10,4) DEFAULT NULL COMMENT '市盈率',
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

    def load_xlsx(self, dt: datetime.datetime):
        """
        下载某一天的明细文件
        :param dt: eg.20200506
        :return:
        """
        dt = dt.strftime("%Y-%m-%d")
        url = self.base_url.format(dt, dt, random.random())
        dirname, filename = os.path.split(os.path.abspath(__file__))
        file_path = os.path.join(dirname, "./data_dir/{}.xlsx".format(dt))
        try:
            urlretrieve(url, file_path, self.callbackfunc)
        except urllib.error.HTTPError:
            logger.warning("不存在这一天的数据{}".format(dt))
        except TimeoutError:
            logger.warning("超时 {} ".format(dt))
        except Exception as e:
            logger.warning("下载失败 : {}".format(e))
            raise Exception
        else:
            return file_path

    def get_history_datas(self):
        """获取深交所全部能拿到的历史数据"""
        _start = datetime.datetime(2020, 5, 24)
        # 网站可以找到的最早时间
        _end = datetime.datetime(2004, 12, 31)
        _dt = _start
        while _dt >= _end:
            logger.info(_dt)
            self.load_xlsx(_dt)
            self.read_xlsx(_dt)
            _dt -= datetime.timedelta(days=1)
            print()

    def start(self):
        self._create_table()

        # 在当天收盘前只能拿到前一天的数据
        self.load_xlsx(self.check_day)
        self.read_xlsx(self.check_day)

        # 在当天收盘后可以拿到今天最新的数据
        self.load_xlsx(self._today)
        self.read_xlsx(self._today)

    def _re_amount(self, amount: str):
        """14,044,875.30 """
        return float(amount.replace(',', ''))

    def select_count(self):
        """获取数据库中当前的插入信息"""
        client = self._init_pool(self.spider_cfg)
        sql = '''
        select count(*) as total from {} where TradingDay = '{}'; 
        '''.format(self.table_name, self.check_day)
        ret = client.select_one(sql).get("total")

        sql2 = '''
        select count(*) as total from {} where TradingDay = '{}';  
        '''.format(self.table_name, self._today)
        ret2 = client.select_one(sql2).get("total")

        msg = "深交所 {} 入库 {} 条 ; {} 入库 {} 条".format(self.check_day, ret, self._today, ret2)
        return msg

    def read_xlsx(self, dt: datetime.datetime):
        dt = dt.strftime("%Y-%m-%d")
        dirname, filename = os.path.split(os.path.abspath(__file__))
        file_path = os.path.join(dirname, "./data_dir/{}.xlsx".format(dt))
        wb = xlrd.open_workbook(file_path)
        # sheet_names = wb.sheet_names()
        ws = wb.sheet_by_name('股票行情')
        _rows = ws.nrows
        print(">>> ", _rows)
        if _rows < 10:
            logger.warning("{} 当天无数据".format(dt))
            self.rm_file(file_path)
            return

        client = self._init_pool(self.spider_cfg)
        items = []
        for idx in range(1, _rows):
            _line = ws.row_values(idx)
            # print(_line)
            item = dict()
            item['TradingDay'] = _line[0]    # 交易日期
            secu_code = _line[1]
            item['SecuCode'] = secu_code     # 证券代码
            inner_code = self.get_inner_code(secu_code)
            if not inner_code:
                raise
            item['InnerCode'] = inner_code
            item['SecuAbbr'] = _line[2]            # 证券简称
            item['PrevClose'] = float(_line[3])    # 前收
            item['Close'] = float(_line[4])        # 今收
            item['RiseFall'] = float(_line[5])     # 升跌(%)
            amount = _line[6]
            item['Amount'] = self._re_amount(amount)      # 成交金额(元)
            item['PERatio'] = self._re_amount(_line[7])   # 市盈率
            items.append(item)
            # self._save(client, item, self.table_name, self.fields)

        logger.info(len(items))
        self._batch_save(client, items, self.table_name, self.fields)
        self.rm_file(file_path)
        client.dispose()

    # def batch_insert_test(self):
    #     """测试"""
    #     client = self._init_pool(self.spider_cfg)
    #     items = [{'TradingDay': '2020-05-22', 'SecuCode': '000001', 'InnerCode': 3, 'SecuAbbr': '平安银行', 'PrevClose': 13.4, 'Close': 12.92, 'RiseFall': -3.58, 'Amount': 1119433491.01, 'PERatio': 9.18}, {'TradingDay': '2020-05-22', 'SecuCode': '000002', 'InnerCode': 6, 'SecuAbbr': '万  科Ａ', 'PrevClose': 25.58, 'Close': 25.16, 'RiseFall': -1.64, 'Amount': 1351549738.66, 'PERatio': 7.32}, {'TradingDay': '2020-05-22', 'SecuCode': '000004', 'InnerCode': 14, 'SecuAbbr': '国农科技', 'PrevClose': 28.5, 'Close': 28.11, 'RiseFall': -1.37, 'Amount': 47612183.69, 'PERatio': 1495.21}, {'TradingDay': '2020-05-22', 'SecuCode': '000005', 'InnerCode': 17, 'SecuAbbr': '世纪星源', 'PrevClose': 2.5, 'Close': 2.5, 'RiseFall': 0.0, 'Amount': 9221078.0, 'PERatio': 17.78}, {'TradingDay': '2020-05-22', 'SecuCode': '000006', 'InnerCode': 20, 'SecuAbbr': '深振业Ａ', 'PrevClose': 4.79, 'Close': 4.68, 'RiseFall': -2.3, 'Amount': 40639782.14, 'PERatio': 7.89}, {'TradingDay': '2020-05-22', 'SecuCode': '000007', 'InnerCode': 23, 'SecuAbbr': '全新好', 'PrevClose': 7.85, 'Close': 8.05, 'RiseFall': 2.55, 'Amount': 58021968.43, 'PERatio': 125.19}, {'TradingDay': '2020-05-22', 'SecuCode': '000008', 'InnerCode': 26, 'SecuAbbr': '神州高铁', 'PrevClose': 3.0, 'Close': 2.96, 'RiseFall': -1.33, 'Amount': 39423770.55, 'PERatio': 18.95}, {'TradingDay': '2020-05-22', 'SecuCode': '000009', 'InnerCode': 28, 'SecuAbbr': '中国宝安', 'PrevClose': 6.78, 'Close': 6.55, 'RiseFall': -3.39, 'Amount': 390400688.62, 'PERatio': 56.08}, {'TradingDay': '2020-05-22', 'SecuCode': '000010', 'InnerCode': 31, 'SecuAbbr': '*ST美丽', 'PrevClose': 4.01, 'Close': 4.01, 'RiseFall': 0.0, 'Amount': 6873765.0, 'PERatio': 70.72}, {'TradingDay': '2020-05-22', 'SecuCode': '000011', 'InnerCode': 34, 'SecuAbbr': '深物业A', 'PrevClose': 8.59, 'Close': 8.29, 'RiseFall': -3.49, 'Amount': 27985153.78, 'PERatio': 6.04}, {'TradingDay': '2020-05-22', 'SecuCode': '000012', 'InnerCode': 38, 'SecuAbbr': '南  玻Ａ', 'PrevClose': 4.62, 'Close': 4.52, 'RiseFall': -2.16, 'Amount': 60775608.01, 'PERatio': 26.17}]
    #     self._batch_save(client, items, self.table_name, self.fields)
    #     # self._save(client, items[0], self.table_name, self.fields)
    #     client.dispose()


if __name__ == "__main__":
    _now = lambda: time.time()
    t1 = _now()
    # SZReport().start()
    SZReport().get_history_datas()
    logger.info("用时: {} s".format(_now() - t1))
