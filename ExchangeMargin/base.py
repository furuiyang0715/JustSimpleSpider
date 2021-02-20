import base64
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import time
import traceback

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
from ExchangeMargin.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarginBase(object):
    # 爬虫库
    spider_cfg = {
        "host": SPIDER_MYSQL_HOST,
        "port": SPIDER_MYSQL_PORT,
        "user": SPIDER_MYSQL_USER,
        "password": SPIDER_MYSQL_PASSWORD,
        "db": SPIDER_MYSQL_DB,
    }

    # 正式库
    product_cfg = {
        "host": PRODUCT_MYSQL_HOST,
        "port": PRODUCT_MYSQL_PORT,
        "user": PRODUCT_MYSQL_USER,
        "password": PRODUCT_MYSQL_PASSWORD,
        "db": PRODUCT_MYSQL_DB,
    }

    # 聚源数据库
    juyuan_cfg = {
        "host": JUY_HOST,
        "port": JUY_PORT,
        "user": JUY_USER,
        "password": JUY_PASSWD,
        "db": JUY_DB,
    }

    # 数据中心库
    dc_cfg = {
        "host": DC_HOST,
        "port": DC_PORT,
        "user": DC_USER,
        "password": DC_PASSWD,
        "db": DC_DB,
    }

    # 测试库
    test_cfg = {
        "host": TEST_MYSQL_HOST,
        "port": TEST_MYSQL_PORT,
        "user": TEST_MYSQL_USER,
        "password": TEST_MYSQL_PASSWORD,
        "db": TEST_MYSQL_DB,
    }

    def __init__(self):
        self.target_table_name = 'stk_mttargetsecurities'
        self.juyuan_table_name = 'MT_TargetSecurities'
        self.is_local = LOCAL
        self.dc_client = None
        self.target_client = None
        self.juyuan_client = None
        self.test_client = None
        self.spider_client = None

    def _init_pool(self, cfg: dict):
        """
        eg.
        conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
        }
        :param cfg:
        :return:
        """
        pool = PyMysqlPoolBase(**cfg)
        return pool

    def _dc_init(self):
        if not self.dc_client:
            self.dc_client = self._init_pool(self.dc_cfg)

    def _target_init(self):
        if not self.target_client:
            self.target_client = self._init_pool(self.product_cfg)

    def _juyuan_init(self):
        if not self.juyuan_client:
            self.juyuan_client = self._init_pool(self.juyuan_cfg)

    def _test_init(self):
        if not self.test_client:
            self.test_client = self._init_pool(self.test_cfg)

    def _spider_init(self):
        if not self.spider_client:
            self.spider_client = self._init_pool(self.spider_cfg)

    def __del__(self):
        for sql_client in (self.dc_client, self.target_client,
                           self.juyuan_client, self.test_client,
                           self.spider_client,
                           ):
            if sql_client:
                sql_client.dispose()

    def contract_sql(self, datas, table: str, update_fields: list):
        if not isinstance(datas, list):
            datas = [datas, ]

        to_insert = datas[0]
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str

        params = []
        for data in datas:
            vs = []
            for k in ks:
                vs.append(data.get(k))
            params.append(vs)

        if update_fields:
            on_update_sql = ''' ON DUPLICATE KEY UPDATE '''
            for update_field in update_fields:
                on_update_sql += '{}=values({}),'.format(update_field, update_field)
            on_update_sql = on_update_sql.rstrip(",")
            sql = base_sql + on_update_sql + """;"""
        else:
            sql = base_sql + ";"
        return sql, params

    def _batch_save(self, sql_pool, to_inserts, table, update_fields):
        try:
            sql, values = self.contract_sql(to_inserts, table, update_fields)
            count = sql_pool.insert_many(sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            logger.info("批量插入的数量是{}".format(count))
            sql_pool.end()
            return count

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

    def _save(self, sql_pool, to_insert, table, update_fields):
        try:
            insert_sql, values = self.contract_sql(to_insert, table, update_fields)
            value = values[0]
            count = sql_pool.insert(insert_sql, value)
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            if count == 1:
                logger.info("插入新数据 {}".format(to_insert))
            elif count == 2:
                logger.info("刷新数据 {}".format(to_insert))
            else:
                logger.info("已有数据 {} ".format(to_insert))
            sql_pool.end()
            return count

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
        self._juyuan_init()
        # 8 是开放式基金
        # 加上 41 是因为 689009
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8, 41) and SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        ret = self.juyuan_client.select_all(sql)
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
        clinet = self._init_pool(self.dc_cfg)
        sql = '''select InnerCode from {} where SecuMarket = {} and TargetCategory = {} and TargetFlag = 1;
        '''.format(self.target_table_name, market, category)
        ret = clinet.select_all(sql)
        ret = [r.get("InnerCode") for r in ret]
        return ret

#     def sync_dc2test(self, table_name):
#         dc_client = self._init_pool(self.dc_cfg)
#         sql = '''select * from {}; '''.format(table_name)
#         datas = dc_client.select_all(sql)
#         test_client = self._init_pool(self.test_cfg)
#         self._batch_save(test_client, datas, table_name, [])
#         dc_client.dispose()
#         test_client.dispose()
#
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
#         if self.is_local:
#             client = self._init_pool(self.test_cfg)
#         else:
#             client = self._init_pool(self.product_cfg)
# #
# #         count = client.delete(sql)
# #         print(count)
# #         client.dispose()
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
#         ret = self._batch_save(client, items, 'stk_mttargetsecurities', [])
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
#         ret = self._batch_save(client, items2, 'stk_mttargetsecurities', [])
#         print(ret)
#
#         # client.dispose()
#
#     # def list_check(self):
#     #     # 今日的清单
#     #     test_client = self._init_pool(self.test_cfg)
#     #     sql = '''select InnerCode from margin_sh_list_spider where ListDate = '2020-06-17' and TargetCategory = 20; '''
#     #     ret = test_client.select_all(sql)
#     #     list_datas = set([r.get("InnerCode") for r in ret])
#     #     print(list_datas)
#     #     test_client.dispose()
#     #
#     #     # dc 的清单
#     #     # dc_client = self._init_pool(self.dc_cfg)
#     #     dc_client = self._init_pool(self.test_cfg)
#     #     sql = '''select InnerCode from stk_mttargetsecurities where TargetFlag = 1 and TargetCategory = 20 and SecuMarket = 83; '''
#     #     ret = dc_client.select_all(sql)
#     #     dc_datas = set([r.get("InnerCode") for r in ret])
#     #     print(dc_datas)
#     #     dc_client.dispose()
#     #
#     #     print(dc_datas == list_datas)
#     #     print(dc_datas - list_datas)
#     #     print(list_datas - dc_datas)
#
#
# if __name__ == "__main__":
#     mb = MarginBase()
#     # mb.sync_dc2test("stk_mttargetsecurities")
#     # mb.select_error_datas()
#     # mb.list_check()
#     mb.select_error_datas()
