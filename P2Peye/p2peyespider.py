import os
import sys
import threading
import time
import traceback
from queue import Queue

import requests
from lxml import html

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import SpiderBase


class P2PEye(SpiderBase):
    """网贷天眼查"""
    def __init__(self):
        super(P2PEye, self).__init__()
        self.web_url = 'https://news.p2peye.com/'
        self.list_queue = Queue()
        self.save_queue = Queue()
        self.table_name = 'p2peye_news'
        self.name = '网贷天眼查'
        self.fields = ['pub_date', 'title', 'link', 'article']
        self.topic_info = {
            'https://news.p2peye.com/xwzx/{}.html': 'listbox92',   # 新闻资讯
            'https://news.p2peye.com/wdzl/{}.html': 'listbox26',   # 专栏文章
            'https://news.p2peye.com/tycj/{}.html': 'listbox75',   # 天眼财经
        }

    def _create_table(self):
        sql = '''
        CREATE TABLE  IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{}'; 
        '''.format(self.table_name, self.name)
        self._spider_init()
        self.spider_client.insert(sql)
        self.spider_client.end()

    def parse_detail(self, link: str):
        try:
            resp = requests.get(link, headers=self.headers, timeout=3)
            if resp and resp.status_code == 200:
                page = resp.text
                doc = html.fromstring(page)
                txt = doc.xpath(".//td[@id='article_content']")[0].text_content()
                txt = self._process_content(txt)
                return txt
        except:
            # traceback.print_exc()
            print("*** ", link)

    def save_items(self):
        while True:
            item = self.save_queue.get()
            try:
                self._save(self.spider_client, item, self.table_name, self.fields)
            except Exception as e:
                print("Parse detail error: {}".format(e))
            self.save_queue.task_done()

    def get_detail(self):
        while True:
            item = self.list_queue.get()
            print(">>> ", item)
            link = item.get("link")
            article = self.parse_detail(link)
            if article:
                item['article'] = article
                self.save_queue.put(item)
            self.list_queue.task_done()

    def get_list(self):
        try:
            resp = requests.get(self.web_url, headers=self.headers, timeout=3)
        except:
            resp = None

        if resp and resp.status_code == 200:
            page = resp.text
            doc = html.fromstring(page)
            topics = doc.xpath(".//div[@class='news-wrap mod-news']")
            for topic in topics:
                news_list = topic.xpath(".//ul[@class='mod-list clearfix']")
                if news_list:
                    for news_part in news_list:
                        normal_news = news_part.xpath(".//li[contains(@class, 'list clearfix')]")
                        for one in normal_news:
                            item = {}
                            url = one.xpath(".//a/@href")[0]
                            title = one.xpath(".//a/@title")[0]
                            pub_date = one.xpath(".//span[@class='time']")[0].text_content()
                            link = "https:" + url if not url.startswith("https") else url
                            item['link'] = link
                            if "/zt/" in link:   # 专题的数据较早了
                                continue
                            item['title'] = title
                            item['pub_date'] = pub_date
                            self.list_queue.put(item)

    def _get_topic_list(self, format_url, id_mark):
        for page in range(2, 50):
            print(id_mark, page)
            url = format_url.format(page)
            try:
                resp = requests.get(url, headers=self.headers, timeout=3)
            except:
                resp = None
            if resp and resp.status_code == 200:
                body = resp.text
                doc = html.fromstring(body)
                news_list = doc.xpath(".//div[@id='{}']".format(id_mark))
                if news_list:
                    news_list = news_list[0]
                    news = news_list.xpath(".//div[@class='mod-leftfixed mod-news clearfix']")
                    for part in news:
                        item = dict()
                        hd = part.xpath(".//div[@class='hd']/a")[0]
                        link = hd.xpath("./@href")[0]
                        link = "https:" + link if not link.startswith("https") else link
                        title = hd.xpath("./@title")[0]
                        pub_date = part.xpath(".//div[@class='fd-left']/span")[-1].text_content()
                        item['link'] = link
                        item['title'] = title
                        item['pub_date'] = pub_date
                        self.list_queue.put(item)

    def get_topic_list(self):
        # 获取专题页文章
        for url, id_mark in self.topic_info.items():
            print(url, id_mark)
            topic_spider = threading.Thread(target=self._get_topic_list, args=(url, id_mark))
            topic_spider.start()

    def start(self):
        t1 = time.time()
        self._create_table()
        self.get_topic_list()

        index_spider = threading.Thread(target=self.get_list)
        index_spider.start()

        for i in range(4):
            datas_parser = threading.Thread(target=self.get_detail)
            datas_parser.start()

        datas_saver = threading.Thread(target=self.save_items)
        datas_saver.start()

        self.list_queue.join()
        self.save_queue.join()
        print("耗时: {}".format(time.time() - t1))


if __name__ == "__main__":
    P2PEye().start()
