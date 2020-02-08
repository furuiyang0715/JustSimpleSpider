# -*- coding: utf-8 -*-

import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from national_statistics.common.sqltools.mysql_pool import MqlPipeline
from national_statistics.govbase import BaseStats
from national_statistics.my_log import logger


class GovStats(BaseStats):
    """ 国家统计局爬虫 最新发布 """
    def __init__(self):
        super(GovStats, self).__init__()

        self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
        self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'

        self.name = '最新发布'
        self.table = 'gov_stats_zxfb'
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)

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

    def start(self):
        # for page in range(0, 24):
        for page in range(0, 1):
            time.sleep(3)
            retry = 3
            while True:
                try:
                    items = self.crawl_list(page)
                    for item in items:
                        time.sleep(1)
                        link = item['link']
                        item['article'] = self.parse_detail_page(link)
                        logger.info(item)
                        self.save_to_mysql(item)
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


# if __name__ == "__main__":
#     t1 = time.time()
#     runner = GovStats()
#     runner.start()
#     logger.info("列表页爬取失败 {}".format(runner.error_list))
#     logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
#     t2 = time.time()
#     logger.info("花费的时间是 {} s".format(t2-t1))
