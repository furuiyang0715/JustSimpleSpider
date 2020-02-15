# -*- coding: utf-8 -*-
import datetime
import logging
import traceback

import pymysql
import requests
from fake_useragent import UserAgent, FakeUserAgentError

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from GovSpiders.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL
from GovSpiders.sql_client import PyMysqlBase
from GovSpiders.sql_pool import PyMysqlPoolBase

logger = logging.getLogger()


class BaseSpider(object):
    def __init__(self):
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        # 是否在本地运行
        self.local = LOCAL

        # selenium 的 Chrome 的相关配置
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
        self.db = MYSQL_DB

        # 以下两个二选一
        # 单个 sql 连接
        self.sql_client = PyMysqlBase(**conf)
        # mysql 连接池
        self.sql_pool = PyMysqlPoolBase(**conf)

        # 请求失败的列表页 url
        self.error_list = []
        # 请求失败的详情页 url
        self.error_detail = []

    def _check_selenium_status(self):
        """
        检查 selenium 服务端的状态
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

    def __del__(self):
        print("爬虫对象销毁时尝试将各类连接关闭 ")
        try:
            self.browser.close()
            self.sql_pool.dispose()
        except:
            pass

    def close(self):
        print("将各类连接尝试关闭 ")
        try:
            self.browser.close()
            self.sql_pool.dispose()
        except:
            pass

    def start(self):
        try:
            self._start()
        except:
            raise
        finally:
            self.close()

    def get_page(self, url, options={}):
        # 封装 带有请求头地请求一个 url 的 text
        try:
            ua = UserAgent()
        # except FakeUserAgentError:
        #     pass
        except:
            pass
        else:
            self.headers = ua.random
        base_headers = {
            'User-Agent': self.headers,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        headers = dict(base_headers, **options)
        # print('Getting', url)
        try:
            r = requests.get(url, headers=headers, timeout=10)
            # print('Getting result', url, r.status_code)
            if r.status_code == 200:
                return r.text
        except ConnectionError:
            # print('Crawling Failed', url)
            return None

    def fetch_page(self, url):
        try:
            self.browser.get(url)
            page = self.browser.page_source
        except:
            print('Crawling Failed', url)
            return None
        else:
            return page

    def contract_sql(self, to_insert):
        """
        根据待插入字典 拼接出对应的 sql 语句
        """
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}`.`{}` '''.format(
            self.db, self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _process_item(self, item):

        # TODO

        return item

    def save_item(self, item):
        to_insert = self._process_item(item)
        insert_sql, values = self.contract_sql(to_insert)

        try:
            self.sql_client.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复", to_insert)
        except:
            traceback.print_exc()
            self.error_detail.append(item.get("link"))


if __name__ == "__main__":
    runner = BaseSpider()

    # runner.sql_client

    test_url = "https://blog.csdn.net/Three_dog/article/details/90298104"
    # page = runner.get_page(test_url)
    # print(page)

    # page = runner.get_page("https://www.taobao.com")
    # print(page)

