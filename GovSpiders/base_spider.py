# -*- coding: utf-8 -*-
import logging
import time
import traceback

import pymysql
import requests
from gne import GeneralNewsExtractor

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from GovSpiders.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL
from GovSpiders.sql_client import PyMysqlBase

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
        self.browser.implicitly_wait(5)

        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.db = MYSQL_DB
        self.sql_client = PyMysqlBase(**conf)
        self.extractor = GeneralNewsExtractor()

        self.error_list = []
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
        try:
            self.browser.close()
        except:
            pass

    def fetch_page(self, url):
        retry = 2
        try:
            self.browser.get(url)
            page = self.browser.page_source
        except:
            retry -= 1
            if retry < 0:
                return
            print('Crawling Failed', url)
            print('try to fetch again')
            time.sleep(3)
            return self.fetch_page(url)
        else:
            return page

    def gne_parse_detail(self, page):
        result = self.extractor.extract(page)
        content = result.get("content")
        return content

    def contract_sql(self, to_insert):
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
        return item

    def save(self, item):
        to_insert = self._process_item(item)
        insert_sql, values = self.contract_sql(to_insert)

        try:
            ret = self.sql_client.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复", to_insert)
            return 1
        except:
            traceback.print_exc()
        else:
            return ret

    def process_list(self, page_num):
        list_retry = 2
        try:
            list_page = self.fetch_page(self.start_url.format(page_num))
            if list_page:
                items = self._parse_list_page(list_page)
            else:
                raise
        except:
            list_retry -= 1
            if list_retry < 0:
                return
            self.process_list(page_num)
        else:
            return items

    def process_detail(self, link):
        detail_retry = 2
        try:
            detail_page = self.fetch_page(link)
            if detail_page:
                article = self._parse_detail_page(detail_page)
            else:
                raise
        except:
            detail_retry -= 1
            if detail_retry < 0:
                return
            self.process_detail(link)
        else:
            return article

    def _start(self, page_num):
        items = self.process_list(page_num)
        if items:
            for item in items:
                link = item["article_link"]
                article = self.process_detail(link)
                if article:
                    item['article_content'] = article
                    print(item)
                    ret = self.save(item)
                    if not ret:
                        self.error_detail.append(item.get("article_link"))
                else:
                    self.error_detail.append(link)
        else:
            self.error_list.append(self.start_url.format(page_num))


if __name__ == "__main__":
    runner = BaseSpider()

    # detail_url = "http://www.pbc.gov.cn/diaochatongjisi/116219/116225/3936095/index.html"
    # detail_page = runner.fetch_page(detail_url)

    # detail_url_with_table = "http://www.pbc.gov.cn/diaochatongjisi/116219/116225/3936088/index.html"
    # detail_page = runner.fetch_page(detail_url_with_table)
    # article = runner.parse_detail(detail_page)
    # print(article)
