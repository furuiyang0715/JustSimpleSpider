import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import time

import requests
import urllib.parse

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from ExchangeMargin.configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                                    SPIDER_MYSQL_DB, PRODUCT_MYSQL_HOST, PRODUCT_MYSQL_PORT, PRODUCT_MYSQL_USER,
                                    PRODUCT_MYSQL_PASSWORD, PRODUCT_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD,
                                    JUY_DB, DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB, SECRET, TOKEN, TEST_MYSQL_HOST,
                                    TEST_MYSQL_PORT, TEST_MYSQL_USER, TEST_MYSQL_PASSWORD, TEST_MYSQL_DB, LOCAL)
from ExchangeMargin.sql_base import Connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarginBase(object):
    spider_conn = Connection(
        host=SPIDER_MYSQL_HOST,
        database=SPIDER_MYSQL_DB,
        user=SPIDER_MYSQL_USER,
        password=SPIDER_MYSQL_PASSWORD,
        port=SPIDER_MYSQL_PORT,
    )

    product_conn = Connection(
        host=PRODUCT_MYSQL_HOST,
        database=PRODUCT_MYSQL_DB,
        user=PRODUCT_MYSQL_USER,
        password=PRODUCT_MYSQL_PASSWORD,
        port=PRODUCT_MYSQL_PORT,
    )

    juyuan_conn = Connection(
        host=JUY_HOST,
        database=JUY_DB,
        user=JUY_USER,
        password=JUY_PASSWD,
        port=JUY_PORT,
    )

    dc_conn = Connection(
        host=DC_HOST,
        database=DC_DB,
        user=DC_USER,
        password=DC_PASSWD,
        port=DC_PORT,
    )

    test_conn = Connection(
        host=TEST_MYSQL_HOST,
        database=TEST_MYSQL_DB,
        user=TEST_MYSQL_USER,
        password=TEST_MYSQL_PASSWORD,
        port=TEST_MYSQL_PORT,
    )

    def __init__(self):
        self.target_table_name = 'stk_mttargetsecurities'
        self.juyuan_table_name = 'MT_TargetSecurities'
        self.is_local = LOCAL

    def _process_content(self, vs):
        """
        去除 4 字节的 utf-8 字符，否则插入 mysql 时会出错
        :param vs:
        :return:
        """
        try:
            # python UCS-4 build的处理方式
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # python UCS-2 build的处理方式
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        params = list()
        for v in vs:
            # 对插入数据进行一些处理
            nv = highpoints.sub(u'', v)
            nv = self._filter_char(nv)
            if nv.strip():     # 不需要在字符串之间保留空格
                params.append(nv)
        # print(params)
        return "".join(params)

    @staticmethod
    def _filter_char(_str):
        """处理特殊的空白字符"""
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            _str = _str.replace(cha, '')
        # _str = _str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        _str = _str.replace(u'\xa0', u'')  # 把 \xa0 直接去除
        return _str

    def get_inner_code(self, secu_code):
        ret = self.inner_code_map.get(secu_code)
        if not ret:
            logger.warning("{} 不存在内部编码".format(secu_code))
            raise
        return ret

    @property
    def inner_code_map(self):
        """
        获取聚源内部编码映射表
        https://dd.gildata.com/#/tableShow/27/column///
        https://dd.gildata.com/#/tableShow/718/column///
        """
        # 8 是开放式基金
        # 加上 41 是因为 689009
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8, 41) and \
        SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        ret = self.juyuan_conn.query(sql)
        info = {}
        for r in ret:
            key = r.get("SecuCode")
            value = r.get('InnerCode')
            info[key] = value
        return info

    def ding(self, msg):
        def get_url():
            timestamp = str(round(time.time() * 1000))
            secret_enc = SECRET.encode('utf-8')
            string_to_sign = '{}\n{}'.format(timestamp, SECRET)
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            url = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(
                TOKEN, timestamp, sign)
            return url

        url = get_url()
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        message = {
            "msgtype": "text",
            "text": {
                "content": "{}@15626046299".format(msg)
            },
            "at": {
                "atMobiles": [
                    "15626046299",
                ],
                "isAtAll": False
            }
        }
        message_json = json.dumps(message)
        resp = requests.post(url=url, data=message_json, headers=header)
        if resp.status_code == 200:
            logger.info("钉钉发送消息成功: {}".format(msg))
        else:
            logger.warning("钉钉消息发送失败")

    def product_dt_datas(self, market, category):
        """
        dc 中的当前选出列表
        :param market:
        :param category:
        :return:
        """
        sql = '''select InnerCode from {} where SecuMarket = {} and TargetCategory = {} and TargetFlag = 1;
        '''.format(self.target_table_name, market, category)
        ret = self.dc_conn.get(sql)
        ret = [r.get("InnerCode") for r in ret]
        return ret

    # * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

    # def sync_dc2test(self, table_name):
    #     sql = '''select * from {}; '''.format(table_name)
    #     datas = self.dc_conn.query(sql)
    #     self.test_conn.batch_insert(datas, table_name, [])

#     def select_error_datas(self):
# #         sql = '''
# #         select id  from stk_mttargetsecurities where SecuMarket = 83 and  InDate = '2020-05-11' \
# # and InnerCode in  (select InnerCode  from stk_mttargetsecurities  group by InnerCode having count(1) > 2);
# #         '''
# #         dc_client = self._init_pool(self.dc_cfg)
# #         ret = dc_client.select_all(sql)
# #         ids = [r.get("id") for r in ret]
# #         print(len(ids))
# #         dc_client.dispose()
# #
# #         sql = '''delete from stk_mttargetsecurities where id in {};'''.format(tuple(ids))
#
#         if self.is_local:
#             client = self.test_conn
#         else:
#             client = self.product_conn
#
#         # count = client.execute(sql)
#         # print(count)
#
#         infos = {
#             230468: '2020-06-10 00:00:00',
#             237992: '2020-06-02 00:00:00',
#             237387: '2020-05-18 00:00:00',
#             237998: '2020-05-21 00:00:00',
#             256016: '2020-05-18 00:00:00',
#             254577: '2020-06-08 00:00:00',
#             256017:  '2020-06-09 00:00:00',
#             268701: '2020-06-16 00:00:00',
#             260383: '2020-06-12 00:00:00',
#          }
#
#         items = []
#         for inner_code, in_date in infos.items():
#             print(inner_code, in_date)
#             item = {'SecuMarket': 83,
#                     "InnerCode": inner_code,
#                     "InDate": in_date,
#                     "TargetCategory": 10,
#                     'TargetFlag': 1,
#                     'UpdateTime': datetime.datetime.now()
#                     }
#             items.append(item)
#         ret = client.batch_insert(items, 'stk_mttargetsecurities', [])
#         print(ret)
#
#         infos2 = {
#             268701: '2020-06-16 00:00:00',
#         }
#         items2 = []
#         for inner_code, in_date in infos2.items():
#             print(inner_code, in_date)
#             item = {'SecuMarket': 83,
#                     "InnerCode": inner_code,
#                     "InDate": in_date,
#                     "TargetCategory": 20,
#                     'TargetFlag': 1,
#                     'UpdateTime': datetime.datetime.now()
#                     }
#             items2.append(item)
#         # ret = self._batch_save(client, items2, 'stk_mttargetsecurities', [])
#         ret = client.batch_insert(items2, 'stk_mttargetsecurities', [])
#         print(ret)
#
    # def list_check(self):
    #     # 今日的清单
    #     sql = '''select InnerCode from margin_sh_list_spider where ListDate = '2020-06-17' and TargetCategory = 20; '''
    #     ret = self.test_conn.query(sql)
    #     list_datas = set([r.get("InnerCode") for r in ret])
    #     print(list_datas)
    #
    #     # dc 的清单
    #     sql = '''select InnerCode from stk_mttargetsecurities where TargetFlag = 1 and TargetCategory = 20 and SecuMarket = 83; '''
    #     ret = self.dc_conn.query(sql)
    #     dc_datas = set([r.get("InnerCode") for r in ret])
    #     print(dc_datas)
    #
    #     print(dc_datas == list_datas)
    #     print(dc_datas - list_datas)
    #     print(list_datas - dc_datas)


# if __name__ == "__main__":
#     mb = MarginBase()
#     # mb.sync_dc2test("stk_mttargetsecurities")
#     # mb.select_error_datas()
#     # mb.list_check()
#     # mb.select_error_datas()
