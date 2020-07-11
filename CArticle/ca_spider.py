import json
import random
import re
import string
import time
import traceback
from urllib.parse import urlencode
import requests
from lxml import html
from retrying import retry

from CArticle.ca_configs import LOCAL_PROXY_URL, PROXY_URL, LOCAL
from base import SpiderBase, logger


class CArticleSpiser(SpiderBase):
    def __init__(self, key):
        super(CArticleSpiser, self).__init__()
        self.key = key
        # 以查询格力电力为例
        self.web_url = 'http://so.eastmoney.com/CArticle/s?keyword=%E6%A0%BC%E5%8A%9B%E7%94%B5%E5%99%A8&pageindex=1'
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
        }
        self.table_name = "eastmoney_carticle"
        self.fields = ['pub_date', 'code', 'title', 'link', 'article']

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

    @retry(stop_max_attempt_number=10)
    def _get(self, url):
        proxies = {'http': self._get_proxy()}
        logger.info("当前获取到的代理是{}".format(proxies))
        resp = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        print(resp)
        return resp

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

    def get_list_page(self, list_url):
        resp = self.get(list_url)
        logger.info("List resp: {}".format(resp))
        if resp and resp.status_code == 200:
            return resp.text
        else:
            logger.warning(resp)
            return None

    def start(self):
        self._spider_init()

        items = []
        # 每个关键词只前推 1 页
        for page in range(1, 2):
            list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
            logger.info(list_url)
            list_page = self.get_list_page(list_url)
            if not list_page:
                logger.warning("列表页请求失败")
                return
            list_infos = self.parse_list(list_page)
            if not list_infos:
                logger.warning("列表页面数据解析失败")
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
                    logger.warning(f"详情页解析失败{link}")
                    continue
                article = self.parse_detail(detail_page)
                item['article'] = article
                print(item)
                items.append(item)
                time.sleep(3)
        print(f'数据个数{len(items)}')
        ret = self._batch_save(self.spider_client, items, self.table_name, self.fields)
        print(f'入库个数{ret}')


if __name__ == "__main__":
    ca = CArticleSpiser(key='视源股份')
    ca.start()
