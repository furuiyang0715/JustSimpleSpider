import datetime
import logging
import re
import sys
import time
import traceback
from random import random

import requests
from gne import GeneralNewsExtractor

sys.path.append("./../")
from takungpao.configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER,
                               SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, PRODUCT_MYSQL_HOST,
                               PRODUCT_MYSQL_PORT, PRODUCT_MYSQL_USER, PRODUCT_MYSQL_PASSWORD,
                               PRODUCT_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB,
                               DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB, LOCAL, LOCAL_PROXY_URL,
                               PROXY_URL)
from takungpao.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Base(object):
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

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }
        self.use_proxy = True  # 是否使用代理的开关
        self.extractor = GeneralNewsExtractor()
        self.fields = ['pub_date', 'link', 'title', 'article', 'source']
        self.table = 'Takungpao'
        # TODO 增量逻辑
        self.by_the_time = datetime.datetime.today() - datetime.timedelta(days=2)

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

    def contract_sql(self, to_insert: dict, table: str, update_fields: list):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str

        # 是否在主键冲突时进行更新插入
        if update_fields:
            on_update_sql = ''' ON DUPLICATE KEY UPDATE '''
            update_vs = []
            for update_field in update_fields:
                on_update_sql += '{}=%s,'.format(update_field)
                update_vs.append(to_insert.get(update_field))
            on_update_sql = on_update_sql.rstrip(",")
            sql = base_sql + on_update_sql + """;"""
            vs.extend(update_vs)
        else:
            sql = base_sql + """;"""

        return sql, tuple(vs)

    def _save(self, sql_pool, to_insert, table, update_fields):
        try:
            insert_sql, values = self.contract_sql(to_insert, table, update_fields)
            count = sql_pool.insert(insert_sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            if count == 1:
                logger.info("插入新数据 {}".format(to_insert))

            elif count == 2:
                logger.info("刷新数据 {}".format(to_insert))

            else:  # 数据已经存在的时候结果为 0
                logger.info("已有数据 {} ".format(to_insert))

            sql_pool.end()
            return count

    def _get_proxy(self):
        if LOCAL:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            random_num = random.randint(0, 10)
            if random_num % 2:
                time.sleep(1)
                return requests.get(PROXY_URL).text.strip()
            else:
                return requests.get(LOCAL_PROXY_URL).text.strip()

    def get(self, url):
        if not self.use_proxy:
            return requests.get(url, headers=self.headers)

        count = 0
        while True:
            count += 1
            if count > 10:
                return None
            try:
                proxy = {"proxy": self._get_proxy()}
                # logger.info("proxy is >> {}".format(proxy))
                resp = requests.get(url, headers=self.headers, proxies=proxy)
            except:
                traceback.print_exc()
                time.sleep(0.5)
            else:
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 404:
                    return None
                else:
                    logger.warning("status_code: >> {}".format(resp.status_code))
                    time.sleep(1)

    def convert_dt(self, time_stamp):
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d

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
        return "".join(params)

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

    def _process_pub_dt(self, pub_date):
        """对 pub_date 的各类时间格式进行统一"""
        current_dt = datetime.datetime.now()
        yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if "小时前" in pub_date:  # eg. 20小时前
            hours = int(pub_date.replace('小时前', ''))
            pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif "昨天" in pub_date:  # eg. 昨天04:24
            pub_date = pub_date.replace('昨天', '')
            pub_date = " ".join([yesterday_dt_str, pub_date])
        elif '前天' in pub_date:  # eg. 前天11:33
            pub_date = pub_date.replace("前天", '')
            pub_date = " ".join([after_yesterday_dt_str, pub_date])
        else:  # eg. 02-29 04:24
            pub_date = str(current_dt.year) + '-' + pub_date
        return pub_date

    def _create_table(self):
        """大公报 建表"""
        sql = '''
        CREATE TABLE IF NOT EXISTS `Takungpao` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `source` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章来源',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大公报-财经类'; 
        '''

        '''
        ALTER TABLE Takungpao ADD source varchar(20) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章来源';
        update Takungpao set source = '大公报'; 
        '''
        client = self._init_pool(self.spider_cfg)
        client.insert(sql)
        client.dispose()

    def start(self):
        self._create_table()

        try:
            self._start()
        except Exception as e:
            raise e
