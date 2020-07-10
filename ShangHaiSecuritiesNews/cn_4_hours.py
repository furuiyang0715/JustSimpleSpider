import json
import random
import re
import string
import time
from urllib.parse import urlencode

import requests as req
from gne import GeneralNewsExtractor
from lxml import html
from base import SpiderBase


class CN4Hours(SpiderBase):
    # 适用于 上证四小时
    def __init__(self):
        super(CN4Hours, self).__init__()
        self.list_url = "http://app.cnstock.com/api/theme/get_theme_list?"
        self.extractor = GeneralNewsExtractor()
        self.table_name = "cn_stock"
        self.fields = ['pub_date', 'title', 'link', 'article']

    def _create_table(self):
        self._spider_init()
        sql = '''
        CREATE TABLE  IF NOT EXISTS `{}` (
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上海证券报'; 
        '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def make_query_params(self, latest_id):
        """
        拼接动态请求参数
        """
        query_params = {
            'maxid': str(0),
            'minid': str(latest_id),   # 这个越大的是越新的内容
            'size': 5,
            'callback': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 20)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def get_zhaiyao(self, url):
        try:
            page = req.get(url, headers=self.headers).text
            doc = html.fromstring(page)
            detail_link = doc.xpath("//div[@class='tcbhd-r']//h1/a/@href")[0]
            return detail_link
        except:
            return None

    def get_detail(self, detail_url):
        try:
            page = req.get(detail_url, headers=self.headers).text
            result = self.extractor.extract(page)
            content = result.get("content")
            return content
        except:
            return None

    def get_count(self):
        params = self.make_query_params(0)
        url = self.list_url + urlencode(params)
        ret = req.get(url, headers=self.headers).text
        json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
        py_data = json.loads(json_data)
        count = py_data.get("item")[0].get("order")
        return count + 1

    def get_list(self):
        count = self.get_count()
        print("网页个数: ", count)
        items = []
        for latest_id in range(count, 0, -5):
            params = self.make_query_params(latest_id)
            url = self.list_url + urlencode(params)
            ret = req.get(url, headers=self.headers).text
            json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
            py_data = json.loads(json_data)
            datas = py_data.get("item")
            if not datas:
                break
            for one in datas:
                item = dict()
                item['pub_date'] = one.get("datetime")
                item['title'] = one.get("title")
                item['zhaiyao'] = 'http://news.cnstock.com/theme,{}.html'.format(one.get("id"))
                items.append(item)
        return items

    def start(self):
        self._create_table()

        self._spider_init()
        items = self.get_list()
        nitems = []
        for item in items:
            zhaiyao_link = item.get('zhaiyao')
            detail_url = self.get_zhaiyao(zhaiyao_link)
            if detail_url:
                item['link'] = detail_url
                item['article'] = self.get_detail(detail_url)
                item.pop("zhaiyao")
                print(item)
                nitems.append(item)

        print("数据量 : ", len(nitems))
        ret = self._batch_save(self.spider_client, nitems, self.table_name, self.fields)
        print("插入个数: ", ret)


if __name__ == "__main__":
    cn4 = CN4Hours()
    cn4.start()
