# -*- coding: utf-8 -*-

import re
import time
import traceback
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from national_statistics.common.sqltools.mysql_pool import MqlPipeline
from national_statistics.govbase import BaseStats
from national_statistics.my_log import logger


class GovStats(BaseStats):
    """ 国家统计局爬虫 新闻发布会 """
    def __init__(self):
        super(GovStats, self).__init__()

        self.first_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index.html"
        self.format_url = "http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index_{}.html"

        self.name = '新闻发布会'
        self.table = 'gov_stats_xwfbh'
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)

    def parse_list_page(self, url):
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

    def start(self):
        # for page in range(0, 5):
        for page in range(0, 1):
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    logger.debug("爬取到的列表页信息是 {}".format(items))
                    for item in items:
                        link = item['link']
                        item['article'], item['pub_date'] = self.parse_detail_page(link)
                        logger.info(item)
                        if item['article']:
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


if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))
