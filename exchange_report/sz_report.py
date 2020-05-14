import xlrd


class SZReport(object):
    """深交所行情爬虫"""
    def __init__(self):
        self.fields = ['TradingDay', 'SecuCode', 'SecuAbbr', 'PrevClose', 'Close', 'RiseFall', 'Amount', 'PERatio']

    def _create_table(self):

        pass

    def start(self):
        wb = xlrd.open_workbook('股票行情.xlsx')
        sheet_names = wb.sheet_names()
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
    SZReport().start()
