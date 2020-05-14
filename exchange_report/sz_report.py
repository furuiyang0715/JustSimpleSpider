import datetime
import os
import random
import urllib
from urllib.request import urlretrieve

import xlrd

from exchange_report.base import ReportBase, logger


class SZReport(ReportBase):
    """深交所行情爬虫"""
    def __init__(self):
        super(SZReport, self).__init__()
        self.fields = ['TradingDay', 'SecuCode', 'InnerCode', 'SecuAbbr', 'PrevClose', 'Close',
                       'RiseFall', 'Amount', 'PERatio']
        self.table_name = 'szse_dailyquote'
        self.base_url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1815_stock&TABKEY=tab1&txtBeginDate={}&txtEndDate={}&radioClass=00%2C20%2C30&txtSite=all&random={}'
        self.check_day = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min) - datetime.timedelta(days=1)

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

    def start(self):
        self._create_table()

        self.load_xlsx(self.check_day)

        self.read_xlsx(self.check_day)

    def _re_amount(self, amount: str):
        """14,044,875.30 """
        return float(amount.replace(',', ''))

    def read_xlsx(self, dt: datetime.datetime):
        dt = dt.strftime("%Y-%m-%d")
        dirname, filename = os.path.split(os.path.abspath(__file__))
        file_path = os.path.join(dirname, "./data_dir/{}.xlsx".format(dt))
        wb = xlrd.open_workbook(file_path)
        # sheet_names = wb.sheet_names()
        ws = wb.sheet_by_name('股票行情')
        _rows = ws.nrows
        client = self._init_pool(self.spider_cfg)
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
            self._save(client, item, self.table_name, self.fields)

        self.rm_file(file_path)
        client.dispose()


if __name__ == "__main__":
    SZReport().start()
