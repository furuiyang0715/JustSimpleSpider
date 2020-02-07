# -*- coding: utf-8 -*-
import sys

import time
import traceback
import requests

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

from national_statistics.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline
from national_statistics.configs import (
    MYSQL_TABLE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
from national_statistics.my_log import logger

ua = UserAgent()


class GovStats(object):
    """
    国家统计局爬虫
    需要爬取的版块有:
        最新发布
        数据解读
        新闻发布会

        ...
    """
    def __init__(self):
        self.local = False
        self.headers = ua.random
        # 根据传入的数据表的名称判断出需要爬取的起始 url 数据
        if MYSQL_TABLE == "gov_stats_zxfb":   # 国家统计局--最新发布
            self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
            self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'
        elif MYSQL_TABLE == "gov_stats_sjjd":   # 国家统计局--数据解读
            self.first_url = "http://www.stats.gov.cn/tjsj/sjjd/index.html"
            self.format_url = "http://www.stats.gov.cn/tjsj/sjjd/index_{}.html"
        elif MYSQL_TABLE == "gov_stats_xwfbh":    # 国家统计局--新闻发布会
            self.first_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index.html"
            self.format_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index_{}.html"
        else:
            raise RuntimeError("请检查数据起始 url")

        # 对于一次无法完全加载完整页面的情况 采用的方式:
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕

        if self.local:  # 本地测试的
            time.sleep(3)
            logger.info("selenoium 服务已就绪")
            self.browser = webdriver.Chrome(desired_capabilities=capa)
        else:   # 线上部署
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
        self.table = MYSQL_TABLE
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)
        # 出错的列表页面
        self.error_list = []
        # 出错的详情页面
        self.detail_error_list = []
        # 单独记录含有 table 的页面 方便单独更新和处理
        self.links_have_table = []

    def _check_selenium_status(self):
        """检查 selenium 服务端的状态"""
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

    def _get_urls(self):
        """
        从当前的 mysql 数据库中获取到全部的文章链接
        :return:
        """
        sl = """select link from {}.{};""".format(self.db, self.table)
        rets = self.sql_client.getAll(sl)
        urls = [r.get("link") for r in rets]
        return urls

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
            (By.XPATH, "//ul[@class='center_list_cont']")))
        lines = ret.find_elements_by_xpath("./*")
        item_list = []
        for line in lines:
            item = {}
            pub_date = line.find_elements_by_xpath(".//font[@class='cont_tit02']")
            if not pub_date:
                continue
            pub_date = pub_date[0].text
            item['pub_date'] = pub_date

            title = line.find_elements_by_xpath(".//font[@class='cont_tit01']")
            if not title:
                continue
            title = title[0].text
            item['title'] = title

            link = line.find_elements_by_xpath(".//p[@class='cont_n']/a")
            if not link:
                continue
            if link:
                link = link[0].get_attribute("href")
                item['link'] = link

            # print(item)
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
                except:
                    try:
                        ret = self.wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[@class='TRS_Editor']")))
                    except:
                        ret = self.wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[@class='center_xilan']")))

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
                    return ''
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

    def first_run(self):
        """
        当前项目是首次进行爬取
        :return:
        """
        # for page in range(0, 5):
        for page in range(0, 1):
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    logger.debug("爬取到的列表页信息是 {}".format(items))
                    for item in items:
                        link = item['link']
                        item['article'] = self.parse_detail_page(link)
                        logger.info(item)
                        if item['article']:
                            self.save_to_mysql(item)
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
    # # 测试爬取列表页
    # demo_list_url = "http://www.stats.gov.cn/tjsj/sjjd/index_1.html"
    # ret = runner.parse_list_page(demo_list_url)
    # print(ret)
    # runner.close()

    # # 测试爬取详情页
    # demo_detail_url = "http://www.stats.gov.cn/tjsj/sjjd/202001/t20200119_1723889.html"
    # ret = runner.parse_detail_page(demo_detail_url)
    # print(ret)
    # runner.close()
    # sys.exit(0)

    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))
