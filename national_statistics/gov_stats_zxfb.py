# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import traceback

import redis
import requests
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
        ...
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        # 根据传入的数据表的名称判断出需要爬取的起始 url 数据
        if MYSQL_TABLE == "gov_stats_zxfb":
            self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
            self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'

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
        self.redis_cli = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE_NAME)
        # redis 中的键名定义规则是 表名 + "_bloom_filter"
        self.bloom = RedisBloomFilter(self.redis_cli, self.table+"_bloom_filter")

        # 出错的列表页面
        self.error_list = []
        # 出错的详情页面
        self.detail_error_list = []
        # 单独记录含有 table 的页面 方便单独更新和处理 
        self.links_have_table = []
        # 爬虫的一个记录器 简单来说就是一个文件
        self.recorder = Recorder()
        # # 上次爬取文章的最新发布时间
        # self.last_dt = None

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
                print(traceback.print_exc())
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

        # # 测试已经全部插入了
        # for url in urls:
        #     if not self.bloom.is_contains(url):
        #         print(url)
        # print("测试完毕")

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
        # print(ret.tag_name)  # ul
        lines = ret.find_elements_by_xpath("./li/a/*")
        item_list = []
        for line in lines: 
            item = {}
            link = line.find_element_by_xpath("./..").get_attribute("href")
            item['link'] = link 
            item['title'] = line.find_element_by_xpath("./font[@class='cont_tit03']").text
            item['pub_date'] = line.find_element_by_xpath("./font[@class='cont_tit02']").text
            # item['article'] = self.parse_detail_page(link)
            item_list.append(item)
            # print("在当前页面获取的数据是:" , item) 
        return item_list

    def parse_detail_page(self, url):
        """
        对文章详情页进行解析
        :param url:
        :return:
        """
        # 文章页面中含有表格的要单独进行处理:
        # for example:  http://www.stats.gov.cn/tjsj/zxfb/201910/t20191021_1704063.html

        retry = 3
        while True: 
            try: 
                self.browser.get(url)
                # 等待直到某个元素出现
                ret = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='TRS_PreAppend']")))
                contents = []
                nodes = ret.find_elements_by_xpath("./*")

                for node in nodes: 
                    if not node.find_elements_by_xpath(".//table"): 
                        c = node.text 
                        if c: 
                            contents.append(c)
                    else: 
                        # logger.warning("去掉 table 中的内容")
                        pass
            except: 
                logger.warning("{} 出错重试".format(url))
                time.sleep(3)
                retry -= 1
                if retry < 0:
                    self.detail_error_list.append(url)
                    # raise RuntimeError("解析详情页始终不成功 ")
                    return
            else: 
                break
        return "\n".join(contents)

    def save_to_mysql(self, item):
        self.pool.save_to_database(item)

    def close(self):
        """
        爬虫程序关闭
        :return:
        """
        this_max_str = self.parse_page_info()
        self.recorder.insert(this_max_str)
        logger.info("爬虫程序已关闭")
        self.sql_client.dispose()
        self.browser.close()

    def parse_page_info(self):
        """
        解析首页 在增量爬取时获取到文章总个数、每页文章数等信息
        :return:
        """
        # TODO 将该捕获机制封装为装饰器
        while True:
            retry = 2
            try:
                items = self.parse_list_page(self.first_url)
            except Exception:
                logger.info("获取首页讯息 失败重试 ")
                time.sleep(5)
                retry -= 1
                if retry < 0:
                    # raise RuntimeError("获取不到首页的讯息")
                    # break
                    logger.warning("获取不到首页的讯息 ")
                    return
            else:
                break
        max_dt = max([datetime.datetime.strptime(item.get("pub_date"), "%Y-%m-%d") for item in items])
        # max_dt = datetime.datetime.strptime(max_dt, "%Y-%m-%d")
        # logger.info(type(max_dt))
        logger.info("当前的最大发布时间是{}".format(max_dt))
        max_dt_str = max_dt.strftime("%Y-%m-%d")
        return max_dt_str

    def first_run(self):
        """
        当前项目是首次进行爬取
        :return:
        """
        for page in range(0, 24):
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    for item in items:
                        link = item['link']
                        if not self.bloom.is_contains(link):
                            item['article'] = self.parse_detail_page(link)
                            self.save_to_mysql(item)
                            self.bloom.insert(link)
                        else:
                            pass
                except Exception:
                    retry -= 1
                    logger.warning("加载出错了,重试, the page is {}".format(page))
                    time.sleep(3)
                    # traceback.print_exc()

                    if retry < 0:
                        self.error_list.append(page)
                        break
                else:
                    logger.info("本页保存成功 {}".format(page))
                    break
        self.close()

    def second_run(self, last_max):
        """
        当前项目是增量进行爬取
        :return:
        """
        for page in range(0, 24):
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    # 找出这一页中的最大时间
                    times = [item.get("pub_date") for item in items]
                    # print(times)  # '2020-02-03', '2020-02-03', '2020-01-31',
                    # print(type(times[0]))   # str

                    times = [datetime.datetime.strptime(t, "%Y-%m-%d") for t in times]
                    # print(times)
                    # print(type(times[0]))  # <class 'datetime.datetime'>

                    # 求出当前页的最大时间 如果该时间都小于上一次的最大时间 说明这一页不用再爬取了 已经爬取过了
                    page_max = max(times)
                    logger.info("当前页的最大时间是{}".format(page_max))
                    logger.info("上次爬取的最大时间是{}".format(last_max))

                    if page_max < last_max:
                        logger.info("增量爬取结束了")
                        return
                    else:
                        for item in items:
                            link = item['link']
                            if not self.bloom.is_contains(link):
                                item['article'] = self.parse_detail_page(link)
                                self.save_to_mysql(item)
                                self.bloom.insert(link)
                            else:
                                pass
                except Exception:
                    retry -= 1
                    logger.warning("加载出错了,重试, the page is {}".format(page))
                    time.sleep(3)
                    if retry < 0:
                        self.error_list.append(page)
                        break
                else:
                    logger.info("本页保存成功 {}".format(page))
                    break

    def start(self):
        logger.info("首先 将已经爬取的链接 insert 到 bloom 过滤器中")
        self.insert_urls()
        last_max = self.recorder.get()

        if not last_max:
            logger.info("首次爬取 ")
            first = True

        else:
            logger.info("增量爬取")
            last_max = datetime.datetime.strptime(last_max, "%Y-%m-%d")
            first = False

        self.second_run(last_max)

        # if first:
        #     self.first_run()
        # else:
        #     self.second_run()


if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))
