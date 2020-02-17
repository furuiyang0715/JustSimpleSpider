import json
import time
import traceback

import jsonpath
import requests
from gne import GeneralNewsExtractor
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from requests.exceptions import ProxyError, Timeout, ConnectionError, ChunkedEncodingError

from qq_A_stock.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL
from qq_A_stock.my_log import logger
from qq_A_stock.sql_base import StoreTool


class qqStock(object):
    def __init__(self):
        self.local = LOCAL
        self.token = "8f6b50e1667f130c10f981309e1d8200"
        self.headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
        self.list_url = "https://pacaio.match.qq.com/irs/rcd?cid=52&token={}" \
       "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&callback=__jp1".format(self.token)
        self.proxy = None
        self.extractor = GeneralNewsExtractor()
        if self.local:
            self.browser = webdriver.Chrome()
        else:
            self._check_selenium_status()
            self.browser = webdriver.Remote(
                command_executor="http://chrome:4444/wd/hub",
                desired_capabilities=DesiredCapabilities.CHROME
            )

        self.browser.implicitly_wait(30)  # 隐性等待，最长等30秒
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.storage = StoreTool(**conf)

    def _check_selenium_status(self):
        """
        检查 selenium 服务端的状态
        :return:
        """
        while True:
            i = 0
            try:
                resp = requests.get("http://chrome:4444/wd/hub/status", timeout=0.5)
            except:
                i += 1
                if i > 10:
                    raise
            else:
                logger.info(resp.text)
                break

    def _get_proxy(self):
        if self.local:
            proxy_url = "http://192.168.0.102:8888/get"
        else:
            proxy_url = "http://172.17.0.5:8888/get"
        r = requests.get(proxy_url)
        proxy = r.text
        return proxy

    def _crawl(self, url, proxy):
        proxies = {'http': proxy}
        r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        return r

    def _get(self, url):
        count = 0
        while True:
            count = count + 1
            try:
                resp = self._crawl(url, self.proxy)
                if resp.status_code == 200:
                    return resp
                elif count >= 5:
                    logger.warning(f'抓取网页{url}最终失败')
                    break
                else:
                    self.proxy = self._get_proxy()
                    logger.info(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
            except (ChunkedEncodingError, ConnectionError, Timeout, UnboundLocalError, UnicodeError, ProxyError):
                self.proxy = self._get_proxy()
                logger.info(f'代理失败,更换代理{self.proxy} \n')

    def _parse_article(self, item, special=False):
        vurl = item.get("link")
        retry = 3
        while True:
            try:
                self.browser.get(vurl)
                body = self.browser.page_source
            except:
                traceback.print_exc()
                retry -= 1
                if retry <= 0:
                    return
                    # break
                time.sleep(5)
            else:
                break

        result = self.extractor.extract(body)
        item['article'] = result.get("content")

        if special:
            item['pub_date'] = result.get("publish_time")
            item['title'] = result.get("title")

        logger.info(item)
        return item

    def _parse_list(self):
        list_resp = self._get(self.list_url)
        if list_resp:
            logger.info("请求主列表页成功 ")
            body = list_resp.text
            body = body.lstrip("__jp1(")
            body = body.rstrip(")")
            body = json.loads(body)
            datas = body.get("data")  # list 数据列表
            # print(datas)

            specials = []
            articles = []

            for data in datas:
                if data.get("article_type") == 120:
                    specials.append(data)
                elif data.get("article_type") == 0:
                    articles.append(data)
                else:
                    logger.info("爬取到预期外的数据{}".format(data))
                    logger.info("爬取到预期外的数据类型{}".format(data.get("article_type")))  # 56 视频类型 不再爬取

            return specials, articles

    def _is_exist(self, vurl):
        ret = self.storage.select_one("select * from `qq_Astock_news` where link = %s;", (vurl))
        if ret:
            return True
        else:
            return False

    def start(self):
        specials, articles = self._parse_list()
        for article in articles:
            item = {}
            vurl = article.get("vurl")
            # 判断 vurl 是否存在
            if not self._is_exist(vurl):
                item['link'] = vurl
                item['pub_date'] = article.get("publish_time")
                item['title'] = article.get("title")
                item = self._parse_article(item)
                if item:
                    self.storage.save(item)
            else:
                logger.info("{} 列表文章 已经爬取过了".format(vurl))

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

                if not self._is_exist(vurl):
                    item['link'] = vurl
                    item = self._parse_article(item, special=True)
                    if item:
                        self.storage.save(item)
                else:
                    logger.info("{} 专题文章 已经爬取过了".format(vurl))

    def __del__(self):
        print("selenium 连接关闭 ")
        self.browser.close()


if __name__ == "__main__":
    now = lambda: time.time()
    t1 = now()
    d = qqStock()

    # proxy = d._get_proxy()
    # print(proxy)

    d.start()
    print(now() - t1)
