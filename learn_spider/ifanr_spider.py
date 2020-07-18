import datetime
import json
import threading
import time
from queue import Queue

import requests
from gne import GeneralNewsExtractor


class IfanrSpider(object):
    def __init__(self):
        self.format_url = 'https://sso.ifanr.com//api/v5/wp/web-feed/?published_at__lte={}&limit=50&offset={}'
        self.list_item_queue = Queue()
        self.page_item_queue = Queue()
        self.extractor = GeneralNewsExtractor()

    def put_list_items(self):
        _now = datetime.datetime.now().strftime("%Y-%m-%d+%H:%M:%S")
        for offset in range(0, 1000, 50):
            url = self.format_url.format(_now, offset)
            resp = requests.get(url)
            if resp and resp.status_code == 200:
                page = resp.text
                datas = json.loads(page).get("objects")
                for data in datas:
                    self.list_item_queue.put(data)
            time.sleep(2)

    def run_use_more_task(self, func, count=1):
        for i in range(0, count):
            t = threading.Thread(target=func)
            t.setDaemon(True)
            t.start()

    def get_list_item(self):
        while True:
            item = self.list_item_queue.get()
            detail_link = item.get("post_url")
            detail_resp = requests.get(detail_link)
            if detail_resp and detail_resp.status_code == 200:
                detail_page = detail_resp.text
                item['post_page'] = detail_page
                self.page_item_queue.put(item)
            else:
                self.list_item_queue.put(item)
            self.list_item_queue.task_done()
            time.sleep(1)

    def extract_content(self, body):
        try:
            result = self.extractor.extract(body)
        except:
            return {}
        else:
            return result

    def parse_list_item(self):
        while True:
            item = self.page_item_queue.get()
            detail_page = item.get("post_page")
            ret = self.extract_content(detail_page)
            data = dict()
            data['title'] = item.get("post_title")
            data['link'] = item.get("post_url")
            data['content'] = ret.get("content")
            data['author'] = item.get("created_by", {}).get("author_url")
            data['pub_date'] = item.get("created_at_format")
            print(data)
            with open('ifanr.txt', 'a', encoding='utf8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
            self.page_item_queue.task_done()

    def start(self):
        self.run_use_more_task(self.put_list_items)
        self.run_use_more_task(self.get_list_item, count=3)
        self.run_use_more_task(self.parse_list_item, count=3)

        # time.sleep(10)
        self.page_item_queue.join()
        self.list_item_queue.join()


if __name__ == "__main__":
    t1 = time.time()
    IfanrSpider().start()
    print(f"耗时: {time.time() - t1} s")
