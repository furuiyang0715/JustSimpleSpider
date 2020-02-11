# -*- coding: utf-8 -*-

import datetime
import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from chinabank.my_log import logger
from chinabank.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL
from chinabank.common.sqltools.mysql_pool import MyPymysqlPool


class BaseSpider(object):
    """
    中国银行爬虫
        爬取两个模块：
        （1） 数据解读
        （2） 新闻发布
    """
    def __init__(self):
        self.local = LOCAL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        if self.local:
            self.browser = webdriver.Chrome()
        else:
            self._check_selenium_status()
            self.browser = webdriver.Remote(
                command_executor="http://chrome:4444/wd/hub",
                desired_capabilities=DesiredCapabilities.CHROME
            )

        self.browser.implicitly_wait(30)  # 隐性等待，最长等30秒

        self.sql_client = MyPymysqlPool(
            {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
            }
        )

        self.db = MYSQL_DB
        self.error_list = []
        self.error_detail = []

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

    def save_to_mysql(self, item):
        self.pool.save_to_database(item)

    def crawl_list(self, offset):
        list_page = self.get_page(self.url.format(offset))
        item_list = self.parse_list_page(list_page)
        return item_list

    def get_page(self, url):
        self.browser.get(url)
        return self.browser.page_source

    def yyyymmdd_date(self, dt: datetime.datetime) -> int:
        return dt.year * 10 ** 4 + dt.month * 10 ** 2 + dt.day

    def __del__(self):
        print("爬虫对象销毁")
        try:
            self.browser.close()
            self.sql_client.dispose()
        except:
            pass

    def close(self):
        print("数据连接关闭")
        try:
            self.browser.close()
            self.sql_client.dispose()
        except:
            pass

    def start(self):
        for j in range(3):
            try:
                self._start()
            except Exception:
                self.close()
                raise
            else:
                self.close()
                break
