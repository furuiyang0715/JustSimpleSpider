# -*- coding: utf-8 -*-
import pprint
import requests

from urllib.parse import urljoin
from lxml import html
from retrying import retry

from GovSpiders.base_spider import GovBaseSpider


class GovStatsShuJuJieDu(GovBaseSpider):
    """国家统计局爬虫 数据解读"""
    def __init__(self):
        super(GovStatsShuJuJieDu, self).__init__()
        self.name = '数据解读'
        self.table_name = 'gov_stats'
        self.first_url = "http://www.stats.gov.cn/tjsj/sjjd/index.html"
        self.format_url = "http://www.stats.gov.cn/tjsj/sjjd/index_{}.html"
        self.detail_base_url = 'http://www.stats.gov.cn/tjsj/sjjd/'
        self.fields = ['pub_date', 'title', 'link', 'article']

    def fetch_page(self, url):

        @retry(stop_max_attempt_number=3)
        def _fetch_page(_url):
            return requests.get(_url, timeout=3).text.encode("ISO-8859-1").decode("utf-8")

        try:
            page = _fetch_page(url)
        except:
            return None
        else:
            return page

    def _get_page_url(self, page_num):
        if page_num == 1:
            return self.first_url
        else:
            return self.format_url.format(page_num)

    def parse_list_page(self, list_page):
        try:
            items = self._parse_list_page(list_page)
        except:
            return []
        else:
            return items

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

    def _create_table(self):
        self._spider_init()
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1714 DEFAULT CHARSET=utf8mb4 COMMENT='国家统计局'; 
        '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def parse_detail_page(self, detail_page):
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

    def start(self):
        self._create_table()
        for page in range(1, 3):
            print(">>> ", page)
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)
            list_page = self.fetch_page(list_url)
            ditems = []
            if list_page:
                items = self.parse_list_page(list_page)
                for item in items:
                    # print(item)
                    link = item['link']
                    detail_page = self.fetch_page(link)
                    if detail_page:
                        article = self.parse_detail_page(detail_page)
                        if article:
                            item['article'] = article
                            print(item)
                            ditems.append(item)
            print("爬取数量: ", len(ditems))
            self._spider_init()
            ret = self._batch_save(self.spider_client, ditems, self.table_name, self.fields)
            print("入库数量:", ret)


if __name__ == "__main__":
    runner = GovStatsShuJuJieDu()
    runner.start()

