# -*- coding: utf-8 -*-
import pprint
from urllib.parse import urljoin

import requests
from lxml import html

from GovSpiders.base_spider import BaseSpider


class GovStatsShuJuJieDu(BaseSpider):
    """国家统计局爬虫 数据解读"""
    def __init__(self):
        super(GovStatsShuJuJieDu, self).__init__()
        self.name = '数据解读'
        # self.table = 'gov_stats_sjjd'
        self.table = 'gov_stats'
        self.first_url = "http://www.stats.gov.cn/tjsj/sjjd/index.html"
        self.format_url = "http://www.stats.gov.cn/tjsj/sjjd/index_{}.html"
        self.detail_base_url = 'http://www.stats.gov.cn/tjsj/sjjd/'

    def fetch_page(self, url):
        page = requests.get(url).text.encode("ISO-8859-1").decode("utf-8")
        # print(page)
        return page

    def _get_page_url(self, page_num):
        if page_num == 1:
            return self.first_url
        else:
            return self.format_url.format(page_num)

    def _parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        lines = doc.xpath("//ul[@class='center_list_cont']/*")
        item_list = []
        for line in lines:
            item = {}
            pub_date = line.xpath(".//font[@class='cont_tit02']")
            if not pub_date:
                continue
            pub_date = pub_date[0].text
            item['pub_date'] = pub_date

            title = line.xpath(".//font[@class='cont_tit01']")
            if not title:
                continue
            title = title[0].text
            item['title'] = title

            link = line.xpath(".//p[@class='cont_n']/a")
            if not link:
                continue
            if link:
                # http://www.stats.gov.cn/tjsj/sjjd/202002/t20200217_1726708.html
                # './202002/t20200217_1726708.html'
                link = link[0].xpath('@href')[0]
                link = urljoin(self.detail_base_url, link)
                # print(link)
                item['link'] = link
            item_list.append(item)
        return item_list

    def _parse_detail_page(self, detail_page):
        doc = html.fromstring(detail_page)
        try:
            ret = doc.xpath("//div[@class='TRS_PreAppend']")
        except:
            try:
                ret = doc.xpath("//div[@class='TRS_Editor']")
            except:
                try:
                    ret = doc.xpath("//div[@class='center_xilan']")
                except:
                    print("未匹配到详情页")
                    ret = None

        if ret:
            contents = []
            nodes = ret[0].xpath("./*")
            for node in nodes:
                if not node.xpath(".//table") and (node.tag != 'table'):
                    c = node.text_content()
                    if c:
                        contents.append(c)
                else:
                    # print("去掉了 table 中的内容")
                    pass
            return "\n".join(contents)
        else:
            return None


if __name__ == "__main__":
    runner = GovStatsShuJuJieDu()
    runner._start(1)


    # list_page = runner.fetch_page("http://www.stats.gov.cn/tjsj/sjjd/index.html")
    # print(list_page)

    # items = runner._parse_list_page(list_page)
    # print(pprint.pformat(items))

    # detail_page = runner.fetch_page("http://www.stats.gov.cn/tjsj/sjjd/202002/t20200217_1726708.html")
    # article = runner._parse_detail_page(detail_page)
    # print(article)


