import requests
from lxml import html

from base import SpiderBase


class P2PEye(SpiderBase):
    """网贷天眼查"""
    def __init__(self):
        super(P2PEye, self).__init__()
        self.web_url = 'https://news.p2peye.com/'

    def get_list(self):
        resp = requests.get(self.web_url, headers=self.headers)
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
                            item['link'] = "https:" + url
                            item['title'] = title
                            item['pub_date'] = pub_date
                            print(item)

    def start(self):
        pass


if __name__ == "__main__":

    pass
