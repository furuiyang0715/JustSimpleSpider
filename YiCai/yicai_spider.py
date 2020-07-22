import datetime
import json
import pprint

import requests
from lxml import html


class YiCai(object):
    def __init__(self):
        self.index_url = 'https://www.yicai.com/'
        self.url = 'https://www.yicai.com/api/ajax/getlatest?page={}&pagesize=25'

    def fetch_detail_page(self, url):
        article = None
        resp = requests.get(url)
        if resp and resp.status_code == 200:
            body = resp.text
            doc = html.fromstring(body)
            try:
                article = doc.xpath(".//div[@class='m-txt']")[0].text_content()
            except:
                pass
        return article

    def get_list_items(self, page):
        items = []
        resp = requests.get(self.url.format(page))
        if resp and resp.status_code == 200:
            body = resp.text
            datas = json.loads(body)
            for one in datas:
                # print(pprint.pformat(one))
                item = dict()
                _date_str = one.get("LastDate")
                _date = datetime.datetime.strptime(_date_str, "%Y-%m-%dT%H:%M:%S")
                item['pub_date'] = _date
                _url = one.get("url")
                if "video" in _url:
                    continue
                link = "https://www.yicai.com" + _url
                item['link'] = link
                item['title'] = one.get("NewsTitle")
                item['source'] = one.get("NewsSource")
                item['author'] = one.get("NewsAuthor")
                detail = self.fetch_detail_page(link)
                item['article'] = detail
                items.append(item)
        return items

    def start(self):
        for page in range(1, 2):
            items = self.get_list_items(page)



if __name__ == "__main__":
    YiCai().start()
