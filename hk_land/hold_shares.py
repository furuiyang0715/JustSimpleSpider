import datetime
import hashlib
import re
import sys
import requests

import opencc

from lxml import html


class HoldShares(object):
    """滬股通及深股通持股紀錄按日查詢"""
    def __init__(self, type):
        self.type = type
        self.url = 'http://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t={}'.format(type)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        self.today = datetime.date.today().strftime("%Y%m%d")
        # 当前只能查询之前一天的记录
        self.check_day = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y/%m/%d")   # 2020/03/29
        self.converter = opencc.OpenCC('t2s')  # 中文繁体转简体
        _type_map = {
            'sh': '沪股通',
            'sz': '深股通',
            'hk': '港股通',
        }
        self.type_name = _type_map.get(self.type)

    @property
    def post_params(self):
        data = {
            '__VIEWSTATE': '/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==',
            '__VIEWSTATEGENERATOR': 'EC4ACD6F',
            '__EVENTVALIDATION': '/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=',
            'today': '{}'.format(self.today),
            'sortBy': 'stockcode',
            'sortDirection': 'asc',
            'alertMsg': '',
            'txtShareholdingDate': '{}'.format(self.check_day),
            'btnSearch': '搜尋',
        }
        return data

    def start_request(self):
        resp = requests.post(self.url, data=self.post_params)
        if resp.status_code == 200:
            body = resp.text
            doc = html.fromstring(body)
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
                simple_secu_name = self.converter.convert(secu_name)
                item['SecuName'] = simple_secu_name
                # 於中央結算系統的持股量
                holding = tr.xpath('./td[3]/div[2]/text()')[0]
                if holding:
                    holding = int(holding.replace(',', ''))
                else:
                    holding = 0
                item['Holding'] = holding
                # 占股的百分比
                POAShares = tr.xpath('./td[4]/div[2]/text()')
                if POAShares:
                    POAShares = float(POAShares[0].replace('%', ''))
                else:
                    POAShares = float(0)
                item['Percent'] = POAShares
                # 类别
                item['category'] = self.type_name
                # 时间
                item['Date'] = date.replace("/", "-")
                # 类别+代码+时间 存成一个 hashID
                d = date.replace('/', '')
                content = item['category'] + item['SecuCode'] + d
                m2 = hashlib.md5()
                m2.update(content.encode('utf-8'))
                item_id = m2.hexdigest()
                item['ItemID'] = item_id
                print(item)
                # 将其存入爬虫数据库 hold_shares_sh hold_shares_sz hold_shares_hk


if __name__ == "__main__":
    for type in ("sh", "sz", "hk"):
        h = HoldShares(type)
        h.start_request()