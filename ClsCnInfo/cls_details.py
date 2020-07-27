import datetime
import os
import sys
import time

import requests
from gne import GeneralNewsExtractor
from lxml import html
from retrying import retry

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import SpiderBase, logger


class ClsDetail(SpiderBase):
    table_name = 'cls_depth_theme'

    def __init__(self):
        super(ClsDetail, self).__init__()
        self.base_url = 'https://www.cls.cn/detail/{}'
        self.extractor = GeneralNewsExtractor()
        self.fields = ['title', 'pub_date', 'article', 'link']

    @retry(stop_max_attempt_number=3)
    def _get(self, url):
        resp = requests.get(url, headers=self.headers, timeout=3)
        return resp

    def get(self, url):
        resp = None
        try:
            resp = self._get(url)
        except:
            return None
        else:
            if resp and resp.status_code == 200:
                return resp.text
            else:
                return None

    def extract_content(self, body):
        """使用 gne 库做解析"""
        try:
            result = self.extractor.extract(body)
        except:
            return ''
        else:
            return result

    def parse_detail(self, body):
        doc = html.fromstring(body)
        # try:
        #     title = doc.xpath(".//div[contains(@class, 'detail-header') or contains(@class, 'detail-banner-title')]")[0].text_content()
        # except:
        #     title = None

        try:
            content = doc.xpath(".//div[contains(@class, 'detail-telegraph-content') or contains(@class, 'detail-content')]")[0].text_content()
        except:
            content = None

        # try:
        #     pub_date = doc.xpath(".//div[contains(@class, 'detail-time')]/span")[0].text_content()
        # except:
        #     pub_date = None

        return {
            # "title": title,
            'article': content,
            # 'pub_date': pub_date,
                }

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `{}`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='财联社-深度及题材' ;
        '''.format(self.table_name)
        self._spider_init()
        self.spider_client.insert(create_sql)
        self.spider_client.end()

    def make_start_num(self):
        sql = 'select link from cls_depth_theme where CREATETIMEJZ = (select max(CREATETIMEJZ) from cls_depth_theme) limit 1;'
        self._spider_init()
        link = self.spider_client.select_one(sql).get("link")
        start_num = int(link.split("/")[-1])
        return start_num

    def start(self):
        start_num = self.make_start_num()
        print(start_num)

        self._create_table()

        items = list()
        for num in range(start_num + 1, start_num + 1000):
            item = dict()
            link = self.base_url.format(num)
            page = self.get(link)
            if not page:
                continue

            res = self.extract_content(page)
            pub_date = res.get("publish_time")
            _pub_date = None
            try:
                _pub_date = datetime.datetime.strptime(pub_date, "%Y年%m月%d日 %H:%M:%S")
            except:
                _pub_date = None
            if not _pub_date:
                try:
                    _pub_date = datetime.datetime.strptime(pub_date, "%Y-%m-%d %H:%M")
                except:
                    pass

            title = res.get("title")
            content = res.get("content")

            if len(title) > 50:
                title = title[:50]

            if "发布广告和不和谐的评论都将会被删除" in content:
                content = self.parse_detail(page)
            content = self._process_content(content)

            if link and title and _pub_date and content:
                item['link'] = link
                item['title'] = title
                item['pub_date'] = _pub_date
                item['article'] = content
                # print(item)
                items.append(item)
                self._save(self.spider_client, item, self.table_name, self.fields)

        # logger.info(f"爬取数据{len(items)}")
        # self._spider_init()
        # ret = self._batch_save(self.spider_client, items, self.table_name, self.fields)
        # logger.info(f"插入数量{ret}")


if __name__ == "__main__":
    ClsDetail().start()
