import re

import requests
from lxml import html


class BaiduNews(object):

    def __init__(self):
        self.index_url = 'http://news.baidu.com/'

        pass

    @staticmethod
    def filter_link(link: str):
        if not link.startswith('http'):
            return False

        return True

    def parse_page_urls(self, url):
        resp = requests.get(url)
        if resp and resp.status_code == 200:
            page = resp.text
            doc = html.fromstring(page)
            links = doc.xpath(".//a/@href")
            links = [link for link in links if self.filter_link(link)]
            print(len(links))
            for link in links:
                print(link)

    def start(self):
        self.parse_page_urls(self.index_url)



BaiduNews().start()
