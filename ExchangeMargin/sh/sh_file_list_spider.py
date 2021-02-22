# 从上交所的爬虫文件中获取到信息
import datetime
import traceback
from functools import cached_property

import requests
import xlrd


from ExchangeMargin.configs import JUY_HOST, JUY_DB, JUY_USER, JUY_PASSWD, JUY_PORT
from ExchangeMargin.sql_base import Connection


class MarginSHFileSpider(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    }

    juyuan_conn = Connection(
        host=JUY_HOST,
        database=JUY_DB,
        user=JUY_USER,
        password=JUY_PASSWD,
        port=JUY_PORT,
    )

    def __init__(self, dt: datetime.datetime):
        self.show_dt = dt
        self.datetime_str = dt.strftime('%Y%m%d')
        self.file_url = f'''http://biz.sse.com.cn//report/rzrq/dbp/zqdbp{self.datetime_str}.xls'''
        # self.file_url = '''http://biz.sse.com.cn//report/rzrq/dbp/zqdbp20210222.xls'''
        print(self.file_url)

    def download_file(self, file_url: str) -> str :
        file_name = file_url.split('/')[-1]
        try:
            resp = requests.get(file_url, timeout=3, headers=self.headers)
        except:
            traceback.print_exc()
            resp = None

        if resp and resp.status_code == 200:
            content = resp.content
            with open(file_name, 'wb') as f:
                f.write(content)
            return file_name
        else:
            print(resp)
            return ''

    @cached_property
    def jyinner_code_map(self):
        # 获取聚源内部编码映射
        # 8 是开放式基金
        # 加上 41 是因为 689009
        print("* " * 50)
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8, 41) and \
        SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        ret = self.juyuan_conn.query(sql)
        info = {}
        for r in ret:
            key = r.get("SecuCode")
            value = r.get('InnerCode')
            info[key] = value
        return info

    def get_jyinner_code(self, secu_code: str) -> str:
        # 获取证券的聚源内部编码
        jyinner_code = self.jyinner_code_map.get(secu_code)
        if jyinner_code is None:

            pass
        else:
            return jyinner_code

    def parse_xl_file(self, file_path: str):
        # 文件分为三个 tab: 融资买入标的证券一览表; 融券卖出标的证券一览表; 融资融券可充抵保证金证券一览表。
        # 融资买入标的证券一览表字段: 证券代码、证券简称
        # 融券卖出标的证券一览表字段: 证券代码、证券简称
        # 融资融券可充抵保证金证券一览表字段: 证券代码、证券简称
        sheet_map = {    # 标的类别：10-融资买入标的，20-融券卖出标的
            '融资买入标的证券一览表': 10,
            '融券卖出标的证券一览表': 20,
        }

        items = []
        wb = xlrd.open_workbook(file_path)
        # for sheet_name in ('融资买入标的证券一览表', '融券卖出标的证券一览表', '融资融券可充抵保证金证券一览表'):
        for sheet_name in ('融资买入标的证券一览表', '融券卖出标的证券一览表'):
            detail = wb.sheet_by_name(sheet_name)

            rows = detail.nrows - 1
            print("总数据量 {}".format(rows))

            head_fields = detail.row_values(0)
            print("表头信息", head_fields)  # 表头信息 ['证券代码', '证券简称']
            head_fields = ['SecuCode', 'SecuAbbr']
            for i in range(1, rows + 1):
                row_val = detail.row_values(i)
                item = dict(zip(head_fields, row_val))
                item['SerialNumber'] = i
                item['ListDate'] = self.show_dt
                item['TargetCategory'] = sheet_map[sheet_name]
                item['InnerCode'] = self.get_jyinner_code(item['SecuCode'])
                item['SecuMarket'] = 83
                print(item)
                items.append(item)
        return items

    def start(self):
        # (1) 下载文件
        file_path = self.download_file(self.file_url)
        if file_path == '':
            return

        # (2) 解析文件数据
        items = self.parse_xl_file(file_path)


if __name__ == '__main__':
    MarginSHFileSpider(datetime.datetime(2021, 2, 1)).start()
