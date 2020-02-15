import json
import random
import re
import string
import sys
import time
import traceback
import pymysql
import requests

from lxml import html
from urllib.parse import urlencode
from gne import GeneralNewsExtractor
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import ProxyError, Timeout, ConnectionError, ChunkedEncodingError

from EastMoneyCarticle.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_TABLE
from EastMoneyCarticle.sql_client import PyMysqlBase

import logging

from EastMoneyCarticle.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CArticle(object):
    def __init__(self, key):
        self.key = key
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",


        }
        self.extractor = GeneralNewsExtractor()
        self.db = MYSQL_DB
        self.table = MYSQL_TABLE
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        # self.sql_client = PyMysqlBase(**conf)
        self.sql_pool = PyMysqlPoolBase(**conf)
        self.proxy = self.get_proxy()
        self.error_detail = []
        self.error_list = []

    def get_proxy(self):
        r = requests.get('http://localhost:8888/get')
        proxy = r.text
        return proxy

    def crawl(self, url, proxy):
        proxies = {'http': proxy}
        r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        return r

    def get(self, url):
        count = 0
        while True:
            count = count + 1
            try:
                resp = self.crawl(url, self.proxy)
                if resp.status_code == 200:
                    return resp
                elif count >= 5:
                    logger.warning(f'抓取网页{url}最终失败')
                    break
                else:
                    self.proxy = self.get_proxy()
                    logger.info(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
            except (ChunkedEncodingError, ConnectionError, Timeout, UnboundLocalError, UnicodeError, ProxyError):
                self.proxy = self.get_proxy()
                logger.info(f'代理失败,更换代理{self.proxy} \n')

    def make_query_params(self, msg, page):
        """
        拼接动态请求参数
        """
        query_params = {
            'type': '8224',  # 该参数表明按时间排序
            'pageindex': str(page),
            'pagesize': str(self.page_size),
            'keyword': msg,
            'name': 'caifuhaowenzhang',
            'cb': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 21)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def get_list(self, list_url):
        resp = self.get(list_url)
        if resp:
            return resp.text
        else:
            self.error_list.append(list_url)

    def get_detail(self, detail_url):
        resp = self.get(detail_url)
        if resp:
            return resp.text
        else:
            self.error_detail.append(detail_url)

    def parse_list(self, list_page):
        try:
            json_data = re.findall(r'jQuery\d{21}_\d{13}\((\{.*?\})\)', list_page)[0]
            list_data = json.loads(json_data).get("Data")
        except:
            return None
        else:
            if list_data:
                return list_data
            else:
                return []

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

    def save(self, to_insert):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            # count = self.sql_client.insert(insert_sql, values)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复 ")
            self.sql_pool.connection.rollback()
        except:
            logger.warning("失败")
            traceback.print_exc()
            self.sql_pool.connection.rollback()
            # 插入失败之后需要进行回滚

        else:
            return count

    def parse_detail(self, detail_page):
        doc = html.fromstring(detail_page)
        article_body = doc.xpath('//div[@class="article-body"]/*')
        contents = []
        for p_node in article_body:
            children = p_node.getchildren()
            children_tags = [child.tag for child in children]
            if children_tags and "img" in children_tags:
                img_links = p_node.xpath("./img/@src")  # list
                contents.append(",".join(img_links))
            else:
                contents.append(p_node.text_content())
        contents = "\r\n".join(contents)
        return contents

    # def process_item(self, item):
    #     return item

    def _exist(self, link):
        ret = self.sql_pool.select_one(f"select * from {self.table} where link = '{link}';")
        if ret:
            return True
        else:
            return False

    def __del__(self):
        print("数据库提交 释放资源")
        self.sql_pool.dispose()

    def _run_page(self, page):
        list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
        list_page = self.get_list(list_url)
        if list_page:
            list_gener = self.parse_list(list_page)  # list
            if not list_gener:
                logger.info(f"{self.key} 爬取完毕 ")
                return

            for data in list_gener:
                item = dict()
                item['code'] = self.key
                link = data.get("ArticleUrl")
                if self._exist(link):
                    logger.info("pass")
                    continue
                item['link'] = data.get("ArticleUrl")
                item['title'] = data.get("Title")
                item['pub_date'] = data.get("ShowTime")
                print("item", item)
                ret = self.save(item)
                if not ret:
                    logger.warning(f"插入失败 {item}")
        return page


class Schedule(object):
    def __init__(self):
        self.keys = ['格力电器', '视源股份', '科大讯飞']

    def insert_list_info(self, key):
        c = CArticle(key)
        now = lambda: time.time()
        t1 = now()
        cur = t1
        for page in range(1, 10000):
            page = c._run_page(page)
            if not page:
                break
            print(f"第 {page} 页, 累计用时 {now() - t1}, 当前页用用时 {now() - cur} ")
            cur = now()
        print(c.error_list)
        print(c.error_detail)

    def run(self):
        self.insert_list_info("科大讯飞")


if __name__ == "__main__":
    schedule = Schedule()
    schedule.run()
