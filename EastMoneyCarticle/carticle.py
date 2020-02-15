import json
import random
import re
import string
import time
import traceback
from urllib.parse import urlencode

import pymysql
from gne import GeneralNewsExtractor
import requests
from lxml import html

from EastMoneyCarticle.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_TABLE
from EastMoneyCarticle.sql_client import PyMysqlBase


class CArticle(object):
    def __init__(self):
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword=%E6%A0%BC%E5%8A%9B%E7%94%B5%E5%99%A8",
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
        self.sql_client = PyMysqlBase(**conf)

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
        return requests.get(list_url, headers=self.headers).text

    def get_detail(self, detail_url):
        return requests.get(detail_url, headers=self.headers).text

    def parse_list(self, list_page):
        try:
            json_data = re.findall(r'jQuery\d{21}_\d{13}\((\{.*?\})\)', list_page)[0]
            list_data = json.loads(json_data).get("Data")
        except:
            return None
        else:
            for data in list_data:
                yield data

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
            count = self.sql_client.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            print("重复 ")
        except:
            print("失败")
            traceback.print_exc()
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

    def process_item(self, item):
        return item

    def start(self):
        key = "格力电器"
        for page in range(1, 2):
            list_url = self.start_url + urlencode(self.make_query_params(key, page))
            list_page = self.get_list(list_url)

            if list_page:
                list_gener = self.parse_list(list_page)
                for data in list_gener:
                    item = {}
                    item['code'] = key
                    item['link'] = data.get("ArticleUrl")
                    item['title'] = data.get("Title")
                    item['pub_date'] = data.get("ShowTime")
                    detail_body = self.get_detail(data.get("ArticleUrl"))
                    article = self.parse_detail(detail_body)
                    if article:
                        item['article'] = article

                        # 将 item 存储到数据库中
                        to_insert = self.process_item(item)
                        print(to_insert)
                        ret = self.save(to_insert)
                        if ret:
                            print("保存成功")


if __name__ == "__main__":
    c = CArticle()
    c.start()