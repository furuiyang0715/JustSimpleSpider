# -*- coding: utf-8 -*-
from urllib.parse import urljoin
from lxml import html
from GovSpiders.gov_stats_sjjd import GovStatsShuJuJieDu


class GovStatsZuiXinFaBu(GovStatsShuJuJieDu):
    """ 国家统计局爬虫 最新发布 """
    def __init__(self):
        super(GovStatsZuiXinFaBu, self).__init__()
        self.name = '最新发布'
        self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
        self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'
        self.detail_base_url = "http://www.stats.gov.cn/"

    def _parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        lines = doc.xpath("//div[@class='center_list']/ul[@class='center_list_contlist']/li/a/*")
        item_list = []
        for line in lines:
            item = {}
            link = line.xpath("./../@href")[0]
            # http://www.stats.gov.cn/tjsj/sjjd/202002/t20200217_1726708.html
            # /tjsj/sjjd/202002/t20200217_1726708.html

            # http://www.stats.gov.cn/tjsj/zxfb/202002/t20200217_1726707.html
            # ./202002/t20200217_1726707.html
            if link.startswith("/tjsj/sjjd"):
                link = urljoin(self.detail_base_url, link)
            else:
                link = "http://www.stats.gov.cn/tjsj/zxfb" + link[1:]
            # print(link)
            item['link'] = link
            item['title'] = line.xpath("./font[@class='cont_tit03']")[0].text_content()
            item['pub_date'] = line.xpath("./font[@class='cont_tit02']")[0].text_content()
            item_list.append(item)
        return item_list


if __name__ == "__main__":
    runner = GovStatsZuiXinFaBu()
    runner.start()
