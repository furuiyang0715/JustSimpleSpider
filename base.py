import base64
import datetime
import hashlib
import hmac
import json
import logging
import os
import random
import re
import sys
import time
import traceback

import requests
import urllib.parse

from retrying import retry

from configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                     SPIDER_MYSQL_DB, PRODUCT_MYSQL_HOST, PRODUCT_MYSQL_PORT, PRODUCT_MYSQL_USER,
                     PRODUCT_MYSQL_PASSWORD, PRODUCT_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD,
                     JUY_DB, DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB, SECRET, TOKEN, LOCAL, LOCAL_PROXY_URL,
                     PROXY_URL)
from sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SpiderBase(object):
    # 数据库基本配置
    spider_cfg = {  # 爬虫库
        "host": SPIDER_MYSQL_HOST,
        "port": SPIDER_MYSQL_PORT,
        "user": SPIDER_MYSQL_USER,
        "password": SPIDER_MYSQL_PASSWORD,
        "db": SPIDER_MYSQL_DB,
    }

    product_cfg = {  # 正式库
        "host": PRODUCT_MYSQL_HOST,
        "port": PRODUCT_MYSQL_PORT,
        "user": PRODUCT_MYSQL_USER,
        "password": PRODUCT_MYSQL_PASSWORD,
        "db": PRODUCT_MYSQL_DB,
    }

    juyuan_cfg = {  # 聚源数据库
        "host": JUY_HOST,
        "port": JUY_PORT,
        "user": JUY_USER,
        "password": JUY_PASSWD,
        "db": JUY_DB,
    }

    dc_cfg = {  # 数据中心库
        "host": DC_HOST,
        "port": DC_PORT,
        "user": DC_USER,
        "password": DC_PASSWD,
        "db": DC_DB,
    }

    def __init__(self):
        self.dc_client = None
        self.product_client = None
        self.juyuan_client = None
        self.spider_client = None

        self.proxy_pool = []
        self.cur_proxy = None
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }

    # 数据库连接初始化
    def _dc_init(self):
        if not self.dc_client:
            self.dc_client = self._init_pool(self.dc_cfg)

    def _product_init(self):
        if not self.product_client:
            self.product_client = self._init_pool(self.product_cfg)

    def _juyuan_init(self):
        if not self.juyuan_client:
            self.juyuan_client = self._init_pool(self.juyuan_cfg)

    def _spider_init(self):
        if not self.spider_client:
            self.spider_client = self._init_pool(self.spider_cfg)

    def __del__(self):
        """结束时销毁已经存在的数据库连接"""
        for _client in (self.dc_client, self.product_client, self.juyuan_client, self.spider_client):
            if _client is not None:
                _client.dispose()

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

    def contract_sql(self, datas, table: str, update_fields: list):
        """拼接 sql 语句"""
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
            # https://stackoverflow.com/questions/12825232/python-execute-many-with-on-duplicate-key-update/12825529#12825529
            # sql = 'insert into A (id, last_date, count) values(%s, %s, %s) on duplicate key update last_date=values(last_date),count=count+values(count)'
            on_update_sql = ''' ON DUPLICATE KEY UPDATE '''
            for update_field in update_fields:
                on_update_sql += '{}=values({}),'.format(update_field, update_field)
            on_update_sql = on_update_sql.rstrip(",")
            sql = base_sql + on_update_sql + """;"""
        else:
            sql = base_sql + ";"
        return sql, params

    def _batch_save(self, sql_pool, to_inserts, table, update_fields):
        """批量插入"""
        if len(to_inserts) == 0:
            logger.warning("批量插入数据量为 0")
            return 0
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

    def _save(self, sql_pool, to_insert, table, update_fields):
        """单个插入"""
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
        """获取聚源内部编码"""
        ret = self.inner_code_map.get(secu_code)
        if not ret:
            logger.warning("{} 不存在内部编码".format(secu_code))
            # raise
        return ret

    @property
    def inner_code_map(self):
        """
        获取聚源内部编码映射表
        https://dd.gildata.com/#/tableShow/27/column///
        https://dd.gildata.com/#/tableShow/718/column///
        """
        # 8 是开放式基金
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8) and SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        # sql = 'SELECT SecuCode,InnerCode from SecuMain;'
        ret = self.juyuan_client.select_all(sql)
        info = {}
        for r in ret:
            key = r.get("SecuCode")
            value = r.get('InnerCode')
            info[key] = value
        return info

    def ding(self, msg):
        """发送钉钉预警消息"""
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

    def _filter_char(self, _str):
        """处理特殊的空白字符"""
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            _str = _str.replace(cha, '')
        # _str = _str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        _str = _str.replace(u'\xa0', u'')  # 把 \xa0 直接去除
        return _str

    def _process_content(self, vs):
        """
        去除 4 字节的 utf-8 字符，否则插入 mysql 时会出错
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

    def callbackfunc(self, blocknum, blocksize, totalsize):
        """
        下载文件的回调函数
        :param blocknum: 已经下载的数据块
        :param blocksize:  数据块的大小
        :param totalsize: 远程文件的大小
        :return:
        """
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        sys.stdout.write("\r%6.2f%%" % percent)
        sys.stdout.flush()

    def rm_file(self, file):
        """清理文件"""
        os.remove(file)
        logger.info("删除文件{}成功".format(file))

    def _process_pub_dt(self, pub_date, cur_year=None):
        """对 pub_date 的各类时间格式进行统一
        eg.
        刚刚
        25分钟前
        今天09:33
        昨天22:02
        07-05 22:14
        ...

        """
        current_dt = datetime.datetime.now()
        current_dt_str = current_dt.strftime("%Y-%m-%d")
        yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if "刚刚" in pub_date:
            return current_dt_str

        if "小时前" in pub_date:  # eg. 20小时前
            hours = int(pub_date.replace('小时前', ''))
            pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif '分钟前' in pub_date:   # eg. 25分钟前
            mimus = int(pub_date.replace('分钟前', ''))
            pub_date = (current_dt - datetime.timedelta(minutes=mimus)).strftime("%Y-%m-%d %H:%M:%S")
        elif '今天' in pub_date:   # eg. 今天09:33
            pub_date = pub_date.replace('今天', '')
            pub_date = " ".join([current_dt_str, pub_date])
        elif "昨天" in pub_date:  # eg. 昨天04:24
            pub_date = pub_date.replace('昨天', '')
            pub_date = " ".join([yesterday_dt_str, pub_date])
        elif '前天' in pub_date:  # eg. 前天11:33
            pub_date = pub_date.replace("前天", '')
            pub_date = " ".join([after_yesterday_dt_str, pub_date])
        else:  # eg. 02-29 04:24
            if cur_year:
                pub_date = str(cur_year) + '-' + pub_date
            else:
                pub_date = str(current_dt.year) + '-' + pub_date
        return pub_date

    def proxy_init(self):
        if LOCAL:
            if not self.proxy_pool:
                print(">>> 扩充")
                self.proxy_pool.extend(requests.get(LOCAL_PROXY_URL).text.split("\r\n"))
        else:
            if not self.proxy_pool:
                self.proxy_pool.extend(requests.get(PROXY_URL).text.split('\r\n'))
                # self.proxy_pool.extend(requests.get(LOCAL_PROXY_URL).text.split("\r\n"))

    def _get_proxy(self):
        self.proxy_init()
        if self.cur_proxy and self.cur_proxy[1]:
            return self.cur_proxy
        self.cur_proxy = random.choice(self.proxy_pool), True
        return self.cur_proxy

    @retry(stop_max_attempt_number=30)
    def _get(self, url):
        time.sleep(2)
        self.cur_proxy = self._get_proxy()
        proxies = {'http': self.cur_proxy[0]}
        logger.info("当前获取到的代理是{}".format(proxies))

        try:
            resp = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        except:
            self.cur_proxy = self.cur_proxy[0], False
            print(f"1 移除{self.cur_proxy[0]}")
            self.proxy_pool.remove(self.cur_proxy[0])
            raise

        if resp.status_code != 200:
            self.cur_proxy = self.cur_proxy[0], False
            print(f"2 移除{self.cur_proxy[0]}")
            self.proxy_pool.remove(self.cur_proxy[0])
            raise

        return resp

    def get(self, url):
        try:
            resp = self._get(url)
        except:
            resp = None
        return resp
