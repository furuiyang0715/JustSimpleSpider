import datetime
import hashlib
import logging
import re
import sys
import traceback
import requests
import opencc
from lxml import html
from hk_land.configs import LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB
from hk_land.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HoldShares(object):
    """滬股通及深股通持股紀錄按日查詢"""
    spider_cfg = {   # 爬虫库
        "host": LOCAL_MYSQL_HOST,
        "port": LOCAL_MYSQL_PORT,
        "user": LOCAL_MYSQL_USER,
        "password": LOCAL_MYSQL_PASSWORD,
        "db": LOCAL_MYSQL_DB,
    }

    product_cfg = {    # 正式库
        "host": LOCAL_MYSQL_HOST,
        "port": LOCAL_MYSQL_PORT,
        "user": LOCAL_MYSQL_USER,
        "password": LOCAL_MYSQL_PASSWORD,
        "db": LOCAL_MYSQL_DB,
    }

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
        _percent_comment_map = {
            'sh': '占于上交所上市及交易的A股总数的百分比(%)',
            'sz': '占于深交所上市及交易的A股总数的百分比(%)',
            'hk': '占已发行股份的百分比(%)',
        }
        self.percent_comment = _percent_comment_map.get(self.type)

        self.table = 'hold_shares_{}'.format(self.type)

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

    def _init_pool(self, cfg):
        pool = PyMysqlPoolBase(**cfg)
        return pool

    def contract_sql(self, to_insert: dict, table: str):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''REPLACE INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _save(self, sql_pool, to_insert, table):
        try:
            insert_sql, values = self.contract_sql(to_insert, table)
            count = sql_pool.insert(insert_sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            logger.info("更入新数据 {}".format(to_insert))
            sql_pool.end()
            return count

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
                # # 类别
                # item['category'] = self.type_name
                # 时间
                item['Date'] = date.replace("/", "-")
                # 类别+代码+时间 存成一个 hashID
                d = date.replace('/', '')
                content = self.type_name + item['SecuCode'] + d
                m2 = hashlib.md5()
                m2.update(content.encode('utf-8'))
                item_id = m2.hexdigest()
                item['ItemID'] = item_id
                spider = self._init_pool(self.spider_cfg)
                self._save(spider, item, self.table)
                # 将其存入爬虫数据库 hold_shares_sh hold_shares_sz hold_shares_hk

    def _create_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS `hold_shares_{}` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `SecuCode` varchar(10) COLLATE utf8_bin NOT NULL COMMENT '股票交易代码',
          `SecuName` varchar(50) COLLATE utf8_bin DEFAULT NULL COMMENT '股票名称',
          `Holding` decimal(19,2) DEFAULT NULL COMMENT '于中央结算系统的持股量',
          `Percent` decimal(9,4) DEFAULT NULL COMMENT '占于{}上市及交易的A股总数的百分比（%）',
          `Date` date DEFAULT NULL COMMENT '日期',
          `ItemID` varchar(50) COLLATE utf8_bin DEFAULT NULL COMMENT 'itemid',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_key` (`SecuCode`,`Date`,`ItemID`),
          KEY `SecuCode` (`SecuCode`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB AUTO_INCREMENT=13280743 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='{}持股记录（HKEX）'; 
        '''.format(self.type, self.percent_comment, self.type_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()


if __name__ == "__main__":
    for type in ("sh", "sz", "hk"):
        h = HoldShares(type)
        h._create_table()
        h.start_request()
