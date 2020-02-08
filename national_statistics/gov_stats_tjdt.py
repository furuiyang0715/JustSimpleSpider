# -*- coding: utf-8 -*-
import time
import traceback

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from national_statistics.common.sqltools.mysql_pool import MqlPipeline
from national_statistics.govbase import BaseStats
from national_statistics.my_log import logger


class GovStats(BaseStats):
    """国家统计局爬虫 统计动态"""
    def __init__(self):
        super(GovStats, self).__init__()

        self.first_url = "http://www.stats.gov.cn/tjgz/tjdt/index.html"
        self.format_url = "http://www.stats.gov.cn/tjgz/tjdt/index_{}.html"

        self.name = '统计动态'
        self.table = 'gov_stats_tjdt'
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)

    def parse_list_page(self, url):
        self.browser.get(url)
        ret = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//ul[@class='center_list_contlist']")))
        lines = ret.find_elements_by_xpath("./*")
        item_list = []
        for line in lines:
            item = {}
            pub_date = line.find_elements_by_xpath(".//font[@class='cont_tit02']")
            if not pub_date:
                continue
            pub_date = pub_date[0].text
            item['pub_date'] = pub_date

            title = line.find_elements_by_xpath(".//font[@class='cont_tit03']")
            if not title:
                continue
            title = title[0].text
            item['title'] = title

            link = line.find_elements_by_xpath("./a")
            if not link:
                continue
            if link:
                link = link[0].get_attribute("href")
                item['link'] = link

            # print(item)
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

    def start(self):
        # for page in range(0, 5):
        for page in range(0, 1):
            time.sleep(3)
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    logger.debug("爬取到的列表页信息是 {}".format(items))
                    for item in items:
                        time.sleep(1)
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


if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    # # 测试爬取列表页
    # demo_list_url = "http://www.stats.gov.cn/tjgz/tjdt/index_1.html"
    # ret = runner.parse_list_page(demo_list_url)
    # print(pprint.pformat(ret))
    # runner.close()

    # 测试爬取详情页
    # demo_detail_url = "http://www.stats.gov.cn/tjgz/tjdt/201912/t20191210_1716854.html"
    # ret = runner.parse_detail_page(demo_detail_url)
    # print(ret)
    # runner.close()
    # sys.exit(0)

    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))
