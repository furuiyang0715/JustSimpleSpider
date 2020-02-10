import json
import pprint
import sys
import time
import traceback
from queue import Queue

import jsonpath
import requests
from fake_useragent import UserAgent
from gne import GeneralNewsExtractor
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from qq_A_stock.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from qq_A_stock.fetch_proxy import proxy_run
from qq_A_stock.my_log import logger
from qq_A_stock.sql_base import StoreTool

ua = UserAgent()


class qqStock(object):
    def __init__(self):
        self.local = True
        self.token = "8f6b50e1667f130c10f981309e1d8200"
        self.headers = ua.random
        self.list_url = "https://pacaio.match.qq.com/irs/rcd?cid=52&token={}" \
       "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&callback=__jp1".format(self.token)
        self.q = Queue()
        self.proxy = None
        self.extractor = GeneralNewsExtractor()
        if self.local:
            self.browser = webdriver.Chrome()
        else:
            self.browser = webdriver.Remote(
                command_executor="http://chrome:4444/wd/hub",
                desired_capabilities=DesiredCapabilities.CHROME
            )

        self.browser.implicitly_wait(5)  # 隐性等待，最长等30秒
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.storage = StoreTool(**conf)

    def update_proxies(self):
        # proxy_run()
        with open("proxies.txt", "r") as f:
            proxies = f.readlines()
        proxies = [p.strip() for p in proxies]
        for proxy in proxies:
            self.q.put(proxy)

    def _get_proxy(self):
        if self.proxy:
            return self.proxy

        elif not self.q.empty():
            self.proxy = self.q.get()
            return self.proxy

        else:
            self.update_proxies()
            self.proxy = self.q.get()
            return self.proxy

    def _get(self, url):
            proxy = self._get_proxy()
            logger.debug("获取到的代理是{}".format(proxy))
            ret = requests.get(url, headers={"User-Agent": ua.random}, proxies={"http": proxy}, timeout=3)
            return ret

    def _parse_article(self, item, special=False):
        vurl = item.get("link")
        while True:
            try:
                self.browser.get(vurl)
                body = self.browser.page_source
            except:
                traceback.print_exc()
                self.proxy = None
                time.sleep(3)
            else:
                break

        result = self.extractor.extract(body)
        item['article'] = result.get("content")

        if special:
            item['pub_date'] = result.get("publish_time")
            item['title'] = result.get("title")

        logger.info(item)
        time.sleep(1)
        return item

    def _parse_article_by_requsets(self, item):
        vurl = item.get("link")

        while True:
            try:
                resp = self._get(vurl)
            except:
                traceback.print_exc()
                self.proxy = None
                time.sleep(3)
            else:
                break

        body = resp.text
        result = self.extractor.extract(body)
        item['article'] = result.get("content")
        item['pub_date'] = result.get("publish_time")
        item['title'] = result.get("title")
        logger.info(item)
        return item

    def _parse_list(self):
        while True:
            try:
                list_resp = self._get(self.list_url)
            except:
                traceback.print_exc()
                self.proxy = None
                time.sleep(3)
            else:
                break

        if list_resp.status_code == 200:
            logger.info("请求主列表页成功 ")
            body = list_resp.text
            body = body.lstrip("__jp1(")
            body = body.rstrip(")")
            body = json.loads(body)
            datas = body.get("data")  # list 数据列表

            specials = []
            articles = []

            for data in datas:
                if data.get("article_type") == 120:
                    specials.append(data)
                elif data.get("article_type") == 0:
                    articles.append(data)
                else:
                    raise Exception("请检查数据")
            return specials, articles

    def start(self):
        specials, articles = self._parse_list()

        for article in articles:
            time.sleep(1)
            item = {}
            vurl = article.get("vurl")
            item['link'] = vurl
            item['pub_date'] = article.get("publish_time")
            item['title'] = article.get("title")

            item = self._parse_article(item)
            self.storage.save(item)

        logger.info("开始处理专题页")

        for special in specials:
            special_id = special.get("app_id")
            special_url = "https://pacaio.match.qq.com/openapi/getQQNewsSpecialListItems?id={}&callback=getSpecialNews".format(special_id)
            ret = self._get(special_url).text
            ret = ret.lstrip("""('getSpecialNews(""")
            ret = ret.rstrip(""")')""")
            jsonobj = json.loads(ret)
            topics = jsonpath.jsonpath(jsonobj, '$..ids..id')
            topic_url = "https://new.qq.com/omn/FIN20200/{}.html"
            for topic in topics:
                item = {}
                vurl = topic_url.format(topic)
                item['link'] = vurl
                item = self._parse_article(item, special=True)
                self.storage.save(item)

    def __del__(self):
        logger.debug("selenium 连接关闭 ")
        self.browser.close()


if __name__ == "__main__":
    now = lambda: time.time()
    t1 = now()
    d = qqStock()
    # proxy = d._get_proxy()
    # print(proxy)
    d.start()
    print(now() - t1)