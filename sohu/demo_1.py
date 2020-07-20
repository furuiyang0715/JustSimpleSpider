import json
import threading
import time
from queue import Queue
import requests
from lxml import html


class SuhuFinance(object):
    def __init__(self):
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
        self.list_item_queue = Queue()
        self.detail_page_queue = Queue()
        self.save_queue = Queue()

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
                content = ret[0].text_content()
                item["article"] = content
                self.save_queue.put(item)
            self.detail_page_queue.task_done()

    def save_items(self):
        while True:
            item = self.save_queue.get()
            item.pop("detail_page")
            print(item)
            self.save_queue.task_done()

    def start(self):
        for page in range(1, 4):
            list_url = self.format_url % page
            self.get_list_items(list_url)
            th = threading.Thread(target=self.get_list_items, args=(list_url, ))
            th.start()

        for i in range(3):
            th = threading.Thread(target=self.get_detail_page)
            th.setDaemon(True)
            th.start()

        for i in range(3):
            th = threading.Thread(target=self.parse_detail_page)
            th.setDaemon(True)
            th.start()

        for i in range(2):
            th = threading.Thread(target=self.save_items)
            th.setDaemon(True)
            th.start()

        self.list_item_queue.join()
        self.detail_page_queue.join()
        self.save_queue.join()


if __name__ == "__main__":
    suhu = SuhuFinance()
    suhu.start()

