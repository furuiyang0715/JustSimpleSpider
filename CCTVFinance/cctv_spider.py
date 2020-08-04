import json
import os
import re
import sys

import requests
from gne import GeneralNewsExtractor

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import SpiderBase


class CCTVFinance(SpiderBase):
    table_name = 'cctvfinance'

    def __init__(self):
        super(CCTVFinance, self).__init__()
        self.url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/economy_1.jsonp?cb=economy'
        self.extractor = GeneralNewsExtractor()
        self.fields = ['title', 'keywords', 'pub_date', 'brief', 'link', 'article']

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `{}`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `keywords` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章关键词',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `brief` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '文章摘要',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='央视网-财经频道';
        '''.format(self.table_name)
        self._spider_init()
        self.spider_client.insert(create_sql)
        self.spider_client.end()

    def extract_content(self, body):
        try:
            result = self.extractor.extract(body)
        except:
            return ''
        else:
            return result

    def parse_detail(self, link):
        resp = requests.get(link, headers=self.headers)
        body = resp.text.encode("ISO-8859-1").decode("utf-8")
        ret = self.extract_content(body)
        content = ret.get("content")
        return content

    def start(self):
        self._create_table()
        resp = requests.get(self.url, headers=self.headers)
        items = []
        if resp.status_code == 200:
            body = resp.text.encode("ISO-8859-1").decode("utf-8")
            datas_str = re.findall(r"economy\((.*)\)", body)[0]
            datas = json.loads(datas_str).get("data").get("list")

            for data in datas:
                item = dict()
                item['title'] = data.get("title")
                item['keywords'] = data.get("keywords")
                item['pub_date'] = data.get("focus_date")
                item['brief'] = data.get('brief')
                link = data.get("url")
                item['link'] = link
                try:
                    content = self.parse_detail(link)
                except:
                    content = None
                if content:
                    item['article'] = content
                    items.append(item)
                    ret = self._save(self.spider_client, item, self.table_name, self.fields)


if __name__ == "__main__":
    CCTVFinance().start()
