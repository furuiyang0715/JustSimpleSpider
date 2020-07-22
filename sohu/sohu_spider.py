import json
import os
import sys
import threading
import time
from queue import Queue
import requests
from lxml import html

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import SpiderBase


class SuhuFinance(SpiderBase):
    table_name = 'SohuFinance'
    dt_benchmark = 'pub_date'

    def __init__(self):
        super(SuhuFinance, self).__init__()
        self.format_url = 'https://v2.sohu.com/integration-api/mix/region/94?\
secureScore=50\
&page=%s\
&size=24\
&pvId=1595213834487tTwv6Ur\
&mpId=0\
&adapter=default\
&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI\
&channel=15\
&requestId=2006120915066717__{}'.format(int(time.time() * 1000))
        self.headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'cookie': 'SUV=2006120915066717; gidinf=x099980107ee11ac7185448570007cf53d61c5dff4ba; __gads=ID=9bb1261cd25d5ccb:T=1593754903:S=ALNI_MZtjTDJngTMkxi5M1Wu9GisGWKLMw; t=1594459538752; IPLOC=CN4400; _muid_=1595214233823230; MTV_SRC=10010001',
        }
        self.name = '搜狐财经'
        self.web_url = 'https://m.sohu.com/ch/15'
        self.list_item_queue = Queue()
        self.detail_page_queue = Queue()
        self.save_queue = Queue()
        self.save_num = 0
        self.fields = ['pub_date', 'title', 'link', 'article']

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

    def get_list_items(self, url):
        resp = requests.get(url, headers=self.headers)
        if resp and resp.status_code == 200:
            datas = json.loads(resp.text).get("data")
            _ts = datas[-1].get("publicTime")
            datas = [data for data in datas if data['resourceType'] == 1]
            for data in datas:
                item = dict()
                # https://m.sohu.com/a/408372635_100141583
                item['link'] = "https://m.sohu.com" + data.get("url")
                item['title'] = data.get("mobileTitle")
                item['pub_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get("publicTime") / 1000))
                self.list_item_queue.put(item)

    def get_detail_page(self):
        while True:
            item = self.list_item_queue.get()
            detail_link = item.get("link")
            detail_page_resp = requests.get(detail_link, headers=self.headers)
            if detail_page_resp and detail_page_resp.status_code == 200:
                detail_page = detail_page_resp.text
                item['detail_page'] = detail_page
                self.detail_page_queue.put(item)
            self.list_item_queue.task_done()
            time.sleep(1)

    def parse_detail_page(self):
        while True:
            item = self.detail_page_queue.get()
            detail_page = item.get('detail_page')
            doc = html.fromstring(detail_page)
            ret = doc.xpath(".//section[@id='articleContent']")
            if ret:
                content = self._process_content(ret[0].text_content())
                item["article"] = content

                if len(item['title']) > 60:
                    item['title'] = item['title'][:60]

                self.save_queue.put(item)
            self.detail_page_queue.task_done()

    def save_items(self):
        while True:
            item = self.save_queue.get()
            item.pop("detail_page")
            ret = self._save(self.spider_client, item, self.table_name, self.fields)
            print(ret, ">>> ", item)
            if ret:
                self.save_num += 1
            self.save_queue.task_done()

    def run_use_more_task(self, func, count=1):
        for i in range(0, count):
            t = threading.Thread(target=func)
            t.setDaemon(True)
            t.start()

    def start(self):
        self._spider_init()

        self._create_table()

        for page in range(1, 4):
            list_url = self.format_url % page
            self.get_list_items(list_url)
            th = threading.Thread(target=self.get_list_items, args=(list_url, ))
            th.start()

        self.run_use_more_task(self.get_detail_page, 3)

        self.run_use_more_task(self.parse_detail_page, 3)

        self.run_use_more_task(self.save_items, 1)

        self.list_item_queue.join()
        self.detail_page_queue.join()
        self.save_queue.join()

        print(f"入库数量: {self.save_num}")


if __name__ == "__main__":
    suhu = SuhuFinance()
    suhu.start()
