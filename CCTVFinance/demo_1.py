import json
import pprint
import re

import requests
from gne import GeneralNewsExtractor
from base import SpiderBase


class CCTVFinance(SpiderBase):

    def __init__(self):
        super(CCTVFinance, self).__init__()
        self.url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/economy_1.jsonp?cb=economy'
        self.extractor = GeneralNewsExtractor()

    def _create_table(self):
        sql = '''
        
        '''
        pass

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


if __name__ == "__main__":
    CCTVFinance().start()
    # link = 'https://jingji.cctv.com/2020/07/30/ARTIhNqfBNxfTbuV158ALTrq200730.shtml'
    # content = CCTVFinance().parse_detail(link)
    # print(content)
