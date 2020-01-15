# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import traceback

import redis
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from national_statistics.common.redistools.bloom_filter_service import RedisBloomFilter
from national_statistics.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline
from national_statistics.configs import MYSQL_TABLE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, \
    REDIS_HOST, REDIS_PORT, REDIS_DATABASE_NAME
from national_statistics.my_log import logger


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
        if MYSQL_TABLE == "gov_stats_zxfb":
            self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
            self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'

        else:
            raise RuntimeError("请检查数据起始 url")
        
        # 对于可以一次加载完成的部分 采用的方式: 
        # self.browser = webdriver.Chrome()
        # 或
        # self.browser = webdriver.Remote(
        #     command_executor="http://{}:4444/wd/hub".format(SELENIUM_HOST),
        #     desired_capabilities=DesiredCapabilities.CHROME
        # )
        # self.browser.implicitly_wait(30)  # 隐性等待，最长等30秒

        # 对于一次无法完全加载完整页面的情况 采用的方式: 
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
        self.browser = webdriver.Chrome(desired_capabilities=capa)  # 关键!记得添加 （本地）
        # self.browser = webdriver.Remote(
        #     command_executor="http://chrome:4444/wd/hub",
        #     desired_capabilities=capa
        # )

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
        self.table = MYSQL_TABLE
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)
        self.redis_cli = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE_NAME)
        # redis 中的键名定义规则是 表名 + "_bloom_filter"
        self.bloom = RedisBloomFilter(self.redis_cli, self.table+"_bloom_filter")

        # 出错的列表页面
        self.error_list = []
        # 出错的详情页面
        self.detail_error_list = []
        # 单独记录含有 table 的页面 方便单独更新和处理 
        self.links_have_table = []

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
                        logger.warning("去掉 table 中的内容")
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
                retry -= 1
                if retry < 0:
                    raise RuntimeError("获取不到首页的讯息")
            else:
                break
        max_dt = max([item.get("pub_date") for item in items])
        # max_dt = datetime.datetime.strptime(max_dt, "%Y-%m-%d")
        # logger.info(type(max_dt))
        logger.info("当前的最大发布时间是{}".format(max_dt))
        return max_dt

    def start(self):
        for page in range(0, 500):
            retry = 3
            while True: 
                try:
                    # 总的来说 是先爬取到列表页 再根据列表页里面的链接去爬取详情页 
                    items = self.crawl_list(page)
                    for item in items:
                        link = item['link']
                        if not self.bloom.is_contains(link):
                            item['article'] = self.parse_detail_page(link)
                            self.save_to_mysql(item)
                            self.bloom.insert(link)
                except Exception:
                    retry -= 1
                    logger.warning("加载出错了,重试, the page is {}".format(page))
                    traceback.print_exc()

                    if retry < 0:
                        self.error_list.append(page)
                        break
                else:
                    logger.info("本页保存成功 {}".format(page))
                    break 

        self.close()
        this_max_dt = self.parse_page_info()
        # TODO 保存本次的时间
        # os.environ.setdefault("LAST_DT", this_max_dt)


if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    runner.start() 
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))
