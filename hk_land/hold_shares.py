import datetime
import hashlib
import re
import sys

import requests
from lxml import html
import opencc

# 滬股通及深股通持股紀錄按日查詢

cc = opencc.OpenCC('t2s')
# s = cc.convert('眾議長與李克強會談')

category_list = ['sh', 'sz', 'hk']
url = 'http://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t={}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
}
today = datetime.date.today().strftime("%Y%m%d")
# print(today)    # 20200330

txtShareholdingDate = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y/%m/%d")
# print(txtShareholdingDate)  # 2020/03/29
data = {
    '__VIEWSTATE': '/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==',
    '__VIEWSTATEGENERATOR': 'EC4ACD6F',
    '__EVENTVALIDATION': '/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=',
    'today': '{}'.format(today),
    'sortBy': 'stockcode',
    'sortDirection': 'asc',
    'alertMsg': '',
    'txtShareholdingDate': '{}'.format(txtShareholdingDate),
    'btnSearch': '搜尋',
}
hu_url = url.format(category_list[0])
resp = requests.post(hu_url, data=data, headers=headers)
# print(resp)
body = resp.text
# print(body)
doc = html.fromstring(body)
# print(doc)
date = doc.xpath('//*[@id="pnlResult"]/h2/span/text()')[0]
# print(date)    # 持股日期: 2020/03/28
date = re.findall(r"持股日期: (\d{4}/\d{2}/\d{2})", date)[0]
# print(date)    # 2020/03/28
trs = doc.xpath('//*[@id="mutualmarket-result"]/tbody/tr')

item = {}
for tr in trs:
    # 股份代码
    secu_code = tr.xpath('./td[1]/div[2]/text()')[0].strip()
    item['SecuCode'] = secu_code

    # 股票名称
    secu_name = tr.xpath('./td[2]/div[2]/text()')[0].strip()
    # print(secu_name)   # 繁体字名称
    simple_secu_name = cc.convert(secu_name)
    # print(simple_secu_name)
    item['SecuName'] = simple_secu_name

    # 於中央結算系統的持股量
    holding = tr.xpath('./td[3]/div[2]/text()')[0]
    if holding:
        holding = int(holding.replace(',', ''))
    else:
        holding = 0
    item['Holding'] = holding

    # 时间
    item['Date'] = date

    # 占股的百分比
    POAShares = tr.xpath('./td[4]/div[2]/text()')[0]
    if POAShares:
        POAShares = float(POAShares.replace('%', ''))
    else:
        POAShares = float(0)
    # print(POAShares)
    item['Percent'] = POAShares

    # 类别
    item['category'] = '沪股通'

    d = item['Date'].replace('/', '')
    # 类别+代码+时间 存成一个 hashID
    content = item['category'] + item['SecuCode'] + d
    m2 = hashlib.md5()
    m2.update(content.encode('utf-8'))
    item_id = m2.hexdigest()
    item['ItemID'] = item_id
    print(item)
    # 将其存入爬虫数据库 hold_shares_sh hold_shares_sz hold_shares_hk

