"""
清洗未击中数据
手动检查进行
"""

import time
import pymysql
import requests as req
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from national_statistics.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline
from national_statistics.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD


def _gen_unhit_items(lst):
    items = []
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
    browser = webdriver.Chrome(desired_capabilities=capa)
    wait = WebDriverWait(browser, 5)  # 等待的最大时间20s

    for url in lst:
        # print(url)
        browser.get(url)
        ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_xilan']")))   # 等待直到某个元素出现
        # ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='TRS_PreAppend']")))   # 等待直到某个元素出现
        # print(ret.text)
        contents = []
        nodes = ret.find_elements_by_xpath("./*")
        # print("nodes{}".format(nodes))

        for node in nodes:
            if not node.find_elements_by_xpath(".//table"):
                c = node.text
                if c:
                    contents.append(c)
            else:
                print("去掉 table 中的内容 ... ")
        # print(contents)
        # print("\n".join(contents))
        # 生成新的待插入数据项
        items.append({"link": url, "article": contents})

    browser.close()
    return items


def gen_uhit_items(lst):
    ret = None
    retry = 2
    while True:
        try:
            ret = _gen_unhit_items(lst)
        except Exception:
            retry -= 1
            if retry < 0:
                break
        else:
            break
    return ret


def mysql_update(db: str, table: str, items: list):
    """
    根据清洗的结果更新数据库
    :param db: 数据库
    :param table: 数据表
    :param items: [{"link": ...., "content": ...}...]
    :return:
    """
    # 创建一个对于 mysql 数据库的连接池对象
    pool = MyPymysqlPool({
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
        })

    # 基于此创建一个可以直接操作数据库的封装对象
    pipeline = MqlPipeline(pool, db, table)
    pipeline.update_datas(items)


ll = ["http://www.stats.gov.cn/tjsj/sjjd/201907/t20190716_1676521.html",
      "http://www.stats.gov.cn/tjsj/sjjd/201812/t20181215_1639746.html "]

its = gen_uhit_items(ll)
# mysql_update("test_furuiyang", "gov_stats_zxfb", its)
mysql_update("little_crawler", "gov_stats_zxfb", its)
