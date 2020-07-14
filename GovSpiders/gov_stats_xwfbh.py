# -*- coding: utf-8 -*-
import re
from lxml import html

from GovSpiders.gov_stats_sjjd import GovStatsShuJuJieDu


class GovStatsXinWenFaBuHui(GovStatsShuJuJieDu):
    """ 国家统计局爬虫 新闻发布会 """
    def __init__(self):
        super(GovStatsXinWenFaBuHui, self).__init__()
        self.name = '新闻发布会'
        self.first_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index.html"
        self.format_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index_{}.html"
        self.detail_base_url = "http://www.stats.gov.cn/tjsj"

    def _parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        ret = doc.xpath("//div[@class='center_list']/ul[@class='center_list_contlist']")
        lines = ret[0].xpath("./li/span[@class='cont_tit']//font[@class='cont_tit03']/*")
        item_list = []
        for line in lines:
            item = {}
            link = line.xpath("./@href")[0]
            link = link.replace("../..", "http://www.stats.gov.cn/tjsj")
            item['link'] = link
            detail_page = self.fetch_page(link)
            item['pub_date'] = self._parse_detail_pub_date(detail_page)
            item['title'] = line.text_content()
            item_list.append(item)
        return item_list

    def _parse_detail_pub_date(self, detail_page):
        doc = html.fromstring(detail_page)
        ret = doc.xpath("//font[@class='xilan_titf']")[0].text_content()
        pub_date = re.findall("发布时间：(\d{4}-\d{2}-\d{2})", ret)[0]
        return pub_date


if __name__ == "__main__":
    runner = GovStatsXinWenFaBuHui()
    runner.start()
