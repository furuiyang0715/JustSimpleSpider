# encoding=utf8
import pprint

import requests
import re
import json


class krSpider(object):
    def __init__(self):
        self.url = 'http://36kr.com/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }

    def get_page_from_url(self):
        response = requests.get(self.url, headers=self.headers)
        return response.content.decode()

    def get_data_from_page(self, page):
        json_str = re.findall('<script>window.initialState=(.*)</script>', page)[0]
        # print(pprint.pformat(json_str))

        dic = json.loads(json_str)
        return dic

    def run(self):
        page = self.get_page_from_url()
        print("<script>window.initialState=" in page)
        data = self.get_data_from_page(page)
        print(type(data))
        print(pprint.pformat(data))


if __name__ == '__main__':
    krs = krSpider()
    krs.run()
