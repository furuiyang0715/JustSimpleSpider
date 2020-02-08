import logging
import time

import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent

from national_statistics.common.sqltools.mysql_pool import MyPymysqlPool
from national_statistics.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from national_statistics.my_log import logger

ua = UserAgent()


class BaseStats(object):
    """ 国家统计局爬虫 基类 """
    def __init__(self):
        self.local = True
        self.headers = ua.random

        # 对于一次无法完全加载完整页面的情况 采用的方式:
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕

        if self.local:  # 本地测试的
            time.sleep(3)
            logger.info("selenoium 服务已就绪")
            self.browser = webdriver.Chrome(desired_capabilities=capa)
        else:  # 线上部署
            self._check_selenium_status()
            self.browser = webdriver.Remote(
                command_executor="http://chrome:4444/wd/hub",
                desired_capabilities=capa
            )

        self.wait = WebDriverWait(self.browser, 5)

        self.sql_client = MyPymysqlPool(
            {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
            }
        )
        self.db = MYSQL_DB

        # 出错的列表页面
        self.error_list = []
        # 出错的详情页面
        self.detail_error_list = []
        # 单独记录含有 table 的页面 方便单独更新和处理
        self.links_have_table = []

    def _check_selenium_status(self):
        """检查线上 selenium 服务端的状态"""
        logger.info("检查 selenium 服务器的状态 ")
        while True:
            i = 0
            try:
                resp = requests.get("http://chrome:4444/wd/hub/status", timeout=0.5)
            except Exception as e:
                time.sleep(0.01)
                i += 1
                if i > 10:
                    raise
            else:
                logger.info(resp.text)
                break

    def crawl_list(self, offset):
        if offset == 0:
            logger.info("要爬取的页面是第一页 {}".format(self.first_url))
            item_list = self.parse_list_page(self.first_url)
        else:
            item_list = self.parse_list_page(self.format_url.format(offset))
        return item_list

    def save_to_mysql(self, item):
        self.pool.save_to_database(item)

    def close(self):
        """
        爬虫程序关闭
        :return:
        """
        logger.info("爬虫程序已关闭")
        self.sql_client.dispose()
        self.browser.close()

    def _get_urls(self):
        """
        从当前的 mysql 数据库中获取到全部的文章链接
        :return:
        """
        sl = """select link from {}.{};""".format(self.db, self.table)
        rets = self.sql_client.getAll(sl)
        urls = [r.get("link") for r in rets]
        return urls

    def insert_urls(self):
        urls = self._get_urls()
        logger.info("要插入的链接个数是 {}".format(len(urls)))

        for url in urls:
            self.bloom.insert(url)

        # # 测试已经全部插入了
        # for url in urls:
        #     if not self.bloom.is_contains(url):
        #         print(url)
        # print("测试完毕")