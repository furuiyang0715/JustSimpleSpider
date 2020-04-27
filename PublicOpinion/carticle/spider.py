import datetime
import json
import logging
import random
import re
import string
import time
import traceback
from urllib.parse import urlencode

import requests
from lxml import html

from configs import (LOCAL_PROXY_URL, PROXY_URL, LOCAL)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseSpider(object):
    def _filter_char(self, test_str):
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            test_str = test_str.replace(cha, '')
        test_str = test_str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        return test_str

    def _process_content(self, vs):
        try:
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        params = list()
        for v in vs:
            nv = highpoints.sub(u'', v)
            nv = self._filter_char(nv)
            params.append(nv)
        return "".join(params)


class CArticleSpiser(BaseSpider):
    def __init__(self, key):
        self.key = key
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
        }
        self.table = "eastmoney_carticle"
        self.error_detail = []
        self.error_list = []
        self.dt_format = '%Y-%m-%d %H:%M:%S'
        self.limit_time = datetime.datetime(2020, 2, 1)
        self.use_proxy = 1

    def make_query_params(self, msg, page):
        query_params = {
            'type': '8224',  # 该参数表明按时间排序
            'pageindex': str(page),
            'pagesize': str(self.page_size),
            'keyword': msg,
            'name': 'caifuhaowenzhang',
            'cb': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 21)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def _get_proxy(self):
        if LOCAL:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            random_num = random.randint(0, 10)
            if random_num % 2:
                time.sleep(1)
                return requests.get(PROXY_URL).text.strip()
            else:
                return requests.get(LOCAL_PROXY_URL).text.strip()

    def _get(self, url):
        if LOCAL:
            r = requests.get(url, headers=self.headers, timeout=3)
        else:
            proxies = {'http': self._get_proxy()}
            logger.info("当前获取到的代理是{}".format(proxies))
            r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        return r

    def get(self, url):
        try:
            resp = self._get(url)
        except:
            resp = None
        return resp

    def parse_detail(self, detail_page):
        try:
            content = self._process_content(self._parse_detail(detail_page))
        except:
            content = None
        return content

    def _parse_detail(self, detail_page):
        doc = html.fromstring(detail_page)
        article_body = doc.xpath('//div[@class="article-body"]/*')
        contents = []
        for p_node in article_body:
            children = p_node.getchildren()
            children_tags = [child.tag for child in children]
            if children_tags and "img" in children_tags:
                img_links = p_node.xpath("./img/@src")  # list
                contents.append(",".join(img_links))
            else:
                contents.append(p_node.text_content())
        contents = "\r\n".join(contents)
        return contents

    def get_detail(self, detail_url):
        resp = self.get(detail_url)
        if resp:
            return resp.text
        else:
            return None

    def parse_list(self, list_page):
        try:
            json_data = re.findall(r'jQuery\d{21}_\d{13}\((\{.*?\})\)', list_page)[0]
            list_data = json.loads(json_data).get("Data")
        except:
            return None
        else:
            if list_data:
                return list_data
            else:
                return []

    def start(self):
        try:
            self._start()
        except:
            traceback.print_exc()

    def get_list(self, list_url):
        resp = self.get(list_url)
        logger.info("List resp: {}".format(resp))
        if resp and resp.status_code == 200:
            return resp.text
        else:
            return None

    def _start(self):
        for page in range(1, 2):
            list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
            logger.info(list_url)
            list_page = self.get_list(list_url)
            if not list_page:
                return
            list_infos = self.parse_list(list_page)
            if not list_infos:
                return
            for data in list_infos:
                item = dict()
                item['code'] = self.key
                link = data.get("ArticleUrl")
                item['link'] = link
                item['title'] = data.get("Title")
                item['pub_date'] = data.get("ShowTime")
                detail_page = self.get_detail(link)
                if not detail_page:
                    continue
                article = self.parse_detail(detail_page)
                item['article'] = article
                print(item)
                time.sleep(10)


if __name__ == "__main__":
    d = CArticleSpiser(key='视源股份')
    d._start()
