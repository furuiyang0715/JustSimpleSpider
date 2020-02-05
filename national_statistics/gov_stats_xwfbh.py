# -*- coding: utf-8 -*-
import datetime
import os
import re
import sys
import time
import traceback

import redis
import requests
import selenium
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from national_statistics.common.redistools.bloom_filter_service import RedisBloomFilter
from national_statistics.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline
from national_statistics.configs import (
    MYSQL_TABLE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, REDIS_PORT,
    REDIS_DATABASE_NAME,
    REDIS_HOST)
from national_statistics.my_log import logger
from national_statistics.sys_info import Recorder


class GovStats(object):
    """
    国家统计局爬虫
    需要爬取的版块有:
        最新发布
        新闻发布会

        ...
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        # 根据传入的数据表的名称判断出需要爬取的起始 url 数据
        if MYSQL_TABLE == "gov_stats_zxfb":   # 国家统计局--最新发布
            self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
            self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'
        elif MYSQL_TABLE == "gov_stats_xwfbh":    # 国家统计局--新闻发布会
            self.first_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index.html"
            self.format_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index_{}.html"
        else:
            raise RuntimeError("请检查数据起始 url")

        # 首先检查 selenium 状态是否准备完毕
        # self._check_selenium_status()
        time.sleep(3)
        logger.info("selenoium 服务已就绪")

        # 对于一次无法完全加载完整页面的情况 采用的方式:
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕

        self.browser = webdriver.Chrome(desired_capabilities=capa)  # 关键!记得添加 （本地）

        # 线上部署
        # self.browser = webdriver.Remote(
        #     command_executor="http://chrome:4444/wd/hub",
        #     desired_capabilities=capa
        # )

        self.wait = WebDriverWait(self.browser, 10)
        self.sql_client = MyPymysqlPool(
            {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
            }
        )
        self.db = MYSQL_DB
        self.table = MYSQL_TABLE
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)
        # self.redis_cli = redis.StrictRedis(host="redis", port=REDIS_PORT, db=REDIS_DATABASE_NAME)
        # self.redis_cli = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE_NAME)
        # redis 中的键名定义规则是 表名 + "_bloom_filter"
        # self.bloom = RedisBloomFilter(self.redis_cli, self.table+"_bloom_filter")

        # 出错的列表页面
        self.error_list = []
        # 出错的详情页面
        self.detail_error_list = []
        # 单独记录含有 table 的页面 方便单独更新和处理
        self.links_have_table = []
        # 爬虫的一个记录器 简单来说就是一个文件
        self.recorder = Recorder()

    def _check_selenium_status(self):
        """
        检查 selenium 服务端的状态
        :return:
        """
        logger.info("检查 selenium 服务器的状态 ")
        while True:
            i = 0
            try:
                # resp = requests.get("http://127.0.0.1:4444/wd/hub/status", timeout=0.5)  # 本地测试用
                resp = requests.get("http://chrome:4444/wd/hub/status", timeout=0.5)
            except Exception as e:
                time.sleep(0.01)
                i += 1
                if i > 10:
                    raise
            else:
                logger.info(resp.text)
                break

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

    def crawl_list(self, offset):
        if offset == 0:
            logger.info("要爬取的页面是第一页 {}".format(self.first_url))
            item_list = self.parse_list_page(self.first_url)
        else:
            item_list = self.parse_list_page(self.format_url.format(offset))
        return item_list

    def parse_list_page(self, url):
        """
        根据 url 对列表页面进行解析
        :param url:
        :return:
        """
        self.browser.get(url)
        ret = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='center_list']/ul[@class='center_list_contlist']")))
        lines = ret.find_elements_by_xpath("./li/span[@class='cont_tit']//font[@class='cont_tit03']/*")
        item_list = []
        for line in lines:
            item = {}
            link = line.get_attribute("href")
            item['link'] = link
            item['title'] = line.text
            item_list.append(item)
        return item_list

    def parse_detail_page(self, url):
        """
        对文章详情页进行解析
        :param url:
        :return:
        """
        retry = 1
        while True:
            try:
                self.browser.get(url)
                # 等待直到某个元素出现
                try:
                    ret = self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='TRS_PreAppend']")))
                except selenium.common.exceptions.TimeoutException:
                    ret = self.wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='TRS_Editor']")))

                ret2 = self.wait.until(EC.presence_of_element_located(
                    # (By.XPATH, "//font[@style='float:left;width:620px;text-align:right;margin-right:60px;']")))
                    (By.XPATH, "//font[@class='xilan_titf']")))

                # pub_date = datetime.datetime.strptime(re.findall("发布时间：(\d{4}-\d{2}-\d{2})", ret2.text)[0], "%Y-%m-%d")
                pub_date = re.findall("发布时间：(\d{4}-\d{2}-\d{2})", ret2.text)[0]
                logger.debug(pub_date)

                contents = []
                nodes = ret.find_elements_by_xpath("./*")

                for node in nodes:
                    if not node.find_elements_by_xpath(".//table") and (node.tag_name != 'table'):
                        c = node.text
                        if c:
                            contents.append(c)
                    else:
                        # logger.warning("去掉 table 中的内容")
                        pass
            except:
                logger.warning("{} 出错重试".format(url))
                # traceback.print_exc()
                time.sleep(3)
                retry -= 1
                if retry < 0:
                    self.detail_error_list.append(url)
                    logger.warning("解析详情页 {} 始终不成功 ".format(url))
                    # raise RuntimeError("解析详情页始终不成功 ")
                    return '', '2020-01-01'
            else:
                break
        return "\n".join(contents), pub_date

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

    def first_run(self):
        """
        当前项目是首次进行爬取
        :return:
        """
        for page in range(0, 5):
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    logger.debug("爬取到的列表页信息是 {}".format(items))
                    for item in items:
                        link = item['link']
                        item['article'], item['pub_date'] = self.parse_detail_page(link)
                        logger.info(item)
                        self.save_to_mysql(item)
                        # self.bloom.insert(link)
                except Exception:
                    traceback.print_exc()
                    retry -= 1
                    logger.warning("加载出错了,重试, the page is {}".format(page))
                    time.sleep(3)
                    if retry < 0:
                        self.error_list.append(page)
                        break
                else:
                    logger.info("本页保存成功 {}".format(page))
                    break

        self.close()

    def start(self):
        self.first_run()


if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))
