# 测试获取详情页面
import pprint
import time
import pymysql
import requests as req
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# 带有表格的详情页 
# lst = ["http://www.stats.gov.cn/tjsj/zxfb/201910/t20191021_1704063.html",
#        "http://www.stats.gov.cn/tjsj/zxfb/201809/t20180917_1623289.html"]

# 在运行之后失败的详情页面 select link  from gov_stats_zxfb where article = '';
ll = ["http://www.stats.gov.cn/tjsj/sjjd/201907/t20190716_1676521.html",
      "http://www.stats.gov.cn/tjsj/sjjd/201812/t20181215_1639746.html "]


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


ret = gen_uhit_items(ll)
print(pprint.pformat(ret))
