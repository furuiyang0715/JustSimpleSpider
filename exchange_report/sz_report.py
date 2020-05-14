import datetime
import random

import xlrd

from exchange_report.base import ReportBase


class SZReport(ReportBase):
    """深交所行情爬虫"""
    def __init__(self):
        super(SZReport, self).__init__()
        self.fields = ['TradingDay', 'SecuCode', 'InnerCode', 'SecuAbbr', 'PrevClose', 'Close',
                       'RiseFall', 'Amount', 'PERatio']
        self.table_name = 'szse_dailyquote'
        self.base_url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1815_stock&TABKEY=tab1&txtBeginDate={}&txtEndDate={}&radioClass=00%2C20%2C30&txtSite=all&random={}'
        self.check_day = (datetime.datetime.combine(datetime.datetime.today(), datetime.time.min) - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.file_url = self.base_url.format(self.check_day, self.check_day, random.random())

    def _create_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuCode` varchar(10) DEFAULT NULL COMMENT '证券代码',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',  
          `SecuAbbr` varchar(100) DEFAULT NULL COMMENT '证券简称',
          `TradingDay` datetime NOT NULL COMMENT '交易日',
          `PrevClose` decimal(10,4) DEFAULT NULL COMMENT '前收价(元)',
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

    def load_file(self):
        """下载昨天的行情文件"""

        pass

    def start(self):
        self._create_table()

        wb = xlrd.open_workbook('股票行情.xlsx')
        # sheet_names = wb.sheet_names()
        ws = wb.sheet_by_name('股票行情')
        _rows = ws.nrows
        for idx in range(0, _rows):
            _line = ws.row_values(idx)
            # print(_line)
            item = dict()
            item['TradingDay'] = _line[0]    # 交易日期
            item['SecuCode'] = _line[1]      # 证券代码
            item['SecuAbbr'] = _line[2]      # 证券简称
            item['PrevClose'] = _line[3]     # 前收
            item['Close'] = _line[4]         # 今收
            item['RiseFall'] = _line[5]      # 升跌(%)
            item['Amount'] = _line[6]        # 成交金额(元)
            item['PERatio'] = _line[7]       # 市盈率
            print(item)


if __name__ == "__main__":
    print(SZReport().file_url)
    # SZReport().start()
