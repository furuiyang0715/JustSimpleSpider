import json
import logging
import pprint
import random
import re
import string
import sys
import time
from urllib.parse import urlencode

import pymysql
import requests as req
from gne import GeneralNewsExtractor

from cnstock.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_TABLE
from cnstock.sql_pool import PyMysqlPoolBase

logger = logging.getLogger()


class CNStock(object):
    def __init__(self, *args, **kwargs):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
                   "Referer": "http://news.cnstock.com/news/sns_yw/index.html",
                   }
        self.headers = headers
        self.list_url = "http://app.cnstock.com/api/waterfall?"
        self.extractor = GeneralNewsExtractor()
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.sql_pool = PyMysqlPoolBase(**conf)
        self.db = MYSQL_DB
        self.table = MYSQL_TABLE
        self.error_list = []
        self.error_detail = []
        self.topic = kwargs.get("topic")

    def make_query_params(self, page):
        """
        拼接动态请求参数
        """
        query_params = {
            # 'colunm': 'qmt-sns_yw',
            'colunm': self.topic,
            'page': str(page),   # 最大 50 页
            'num': str(10),
            'showstock': str(0),
            'callback': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 20)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def get_list(self):
        for page in range(0, 1000):
            print(page)
            params = self.make_query_params(page)
            url = self.list_url + urlencode(params)
            # print(url)
            ret = req.get(url, headers=self.headers).text
            # print(ret)

            json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
            # print(json_data)

            py_data = json.loads(json_data)
            # print(py_data)

            datas = py_data.get("data", {}).get("item")
            if not datas:
                break
            for one in datas:
                item = dict()
                item['pub_date'] = one.get("time")
                item['title'] = one.get("title")
                item['link'] = one.get("link")
                yield item

    def get_detail(self, detail_url):
        page = req.get(detail_url, headers=self.headers).text
        result = self.extractor.extract(page)
        content = result.get("content")
        return content

    def contract_sql(self, to_insert):
        """
        根据待插入字典 拼接出对应的 sql 语句
        """
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}`.`{}` '''.format(
            self.db, self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _save(self, to_insert):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            # count = self.sql_client.insert(insert_sql, values)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复 ")
            self.sql_pool.connection.rollback()
        except:
            logger.warning("失败")
            # traceback.print_exc()
            # self.error_detail.append(to_insert.get("link"))
            self.sql_pool.connection.rollback()
            # 插入失败之后需要进行回滚
        else:
            return count

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass

    def start(self):
        count = 0
        for item in self.get_list():
            # print(item, type(item))
            if item:
                link = item.get('link')
                if not link or link == "null":
                    continue
                item['article'] = self.get_detail(link)
                print(item)
                ret = self._save(item)
                count += 1
                if ret:
                    # print("insert ok ")
                    pass
                else:
                    self.error_detail.append(item.get("link"))
                    # print("insert fail")

                if count > 10:
                    self.sql_pool.connection.commit()
                    # print("提交")
                    count = 0


# runner = CNStock(topic='qmt-sns_yw')   #  宏观
# runner = CNStock(topic='qmt-sns_jg')   # 金融
runner = CNStock(topic="qmt-scp_gsxw")   # 公司聚焦


runner.start()