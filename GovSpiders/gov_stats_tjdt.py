# -*- coding: utf-8 -*-
import pprint
from urllib.parse import urljoin

from lxml import html

from GovSpiders.gov_stats_sjjd import GovStatsShuJuJieDu


class GovStatsTongJiDongTai(GovStatsShuJuJieDu):
    """国家统计局爬虫 统计动态"""
    def __init__(self):
        super(GovStatsTongJiDongTai, self).__init__()
        self.name = '统计动态'
        # self.table = 'gov_stats_tjdt'
        self.table = 'gov_stats'
        self.first_url = "http://www.stats.gov.cn/tjgz/tjdt/index.html"
        self.format_url = "http://www.stats.gov.cn/tjgz/tjdt/index_{}.html"
        self.detail_base_url = "http://www.stats.gov.cn/tjgz/tjdt/"

    def _parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        lines = doc.xpath("//ul[@class='center_list_contlist']/*")
        item_list = []
        for line in lines:
            item = {}
            pub_date = line.xpath(".//font[@class='cont_tit02']")
            if not pub_date:
                continue
            pub_date = pub_date[0].text
            item['pub_date'] = pub_date

            title = line.xpath(".//font[@class='cont_tit03']")
            if not title:
                continue
            title = title[0].text
            item['title'] = title

            link = line.xpath("./a")
            if not link:
                continue
            if link:
                link = link[0].xpath('@href')[0]
                # http://www.stats.gov.cn/tjgz/tjdt/201912/t20191213_1717372.html
                # print(link)  # './201912/t20191213_1717372.html'
                link = urljoin(self.detail_base_url, link)
                item['link'] = link
            # print(item)
            item_list.append(item)
        return item_list


if __name__ == "__main__":
    runner = GovStatsTongJiDongTai()
    # demo_list_url = "http://www.stats.gov.cn/tjgz/tjdt/index_1.html"
    # list_page = runner.fetch_page(demo_list_url)
    # ret = runner._parse_list_page(list_page)
    # print(pprint.pformat(ret))

    # demo_detail_url = "http://www.stats.gov.cn/tjgz/tjdt/201912/t20191210_1716854.html"
    # detail_page = runner.fetch_page(demo_detail_url)
    # ret = runner._parse_detail_page(detail_page)
    # print(ret)

    runner.start(1)
