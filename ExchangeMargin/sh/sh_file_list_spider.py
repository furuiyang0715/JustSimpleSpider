# 从上交所的爬虫文件中获取到信息
import traceback

import requests
import xlrd

file_url = '''http://biz.sse.com.cn//report/rzrq/dbp/zqdbp20210222.xls'''

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
}

file_name = 'zqdbp20210222.xls'
# (1) 下载文件
# try:
#     resp = requests.get(file_url, timeout=3, headers=headers)
# except:
#     traceback.print_exc()
#     resp = None
#
# if resp and resp.status_code == 200:
#     content = resp.content
#     with open(file_name, 'wb') as f:
#         f.write(content)
# else:
#     print(resp)

# (2) 解析文件数据
# 文件分为三个 tab: 融资买入标的证券一览表; 融券卖出标的证券一览表; 融资融券可充抵保证金证券一览表。
# 融资买入标的证券一览表字段: 证券代码、证券简称
# 融券卖出标的证券一览表字段: 证券代码、证券简称
# 融资融券可充抵保证金证券一览表字段: 证券代码、证券简称
wb = xlrd.open_workbook(file_name)
for sheet_name in ('融资买入标的证券一览表', '融券卖出标的证券一览表',  '融资融券可充抵保证金证券一览表'):
    detail = wb.sheet_by_name(sheet_name)

    rows = detail.nrows - 1
    print("总数据量 {}".format(rows))

    head_fields = detail.row_values(0)
    print("表头信息", head_fields)   # 表头信息 ['证券代码', '证券简称']
    head_fields = ['SecuCode', 'SecuAbbr']

    items = []
    for i in range(1, rows + 1):
        row_val = detail.row_values(i)
        item = dict(zip(head_fields, row_val))
        item['SerialNumber'] = i
        # item['ListDate'] = show_dt
        # item['TargetCategory'] = 10
        # item['InnerCode'] = inner_code
        item['SecuMarket'] = 83

        items.append(item)

