# 测试获取列表页面
import datetime
import re
import sys
import time

import requests as req
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities

from selenium.webdriver.support import expected_conditions as EC

# browser = webdriver.Chrome()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
browser = webdriver.Chrome(desired_capabilities=capa)  # 关键!记得添加
wait = WebDriverWait(browser, 3)  # 等待的最大时间


# # 测试爬取国家统计局 最新发布的列表页页面
# browser.get("http://www.stats.gov.cn/tjsj/zxfb/")
# ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_list']/ul[@class='center_list_contlist']")))   # 等待直到某个元素出现
# print(ret.tag_name)  # ul
# lines = ret.find_elements_by_xpath("./li/a/*")
# for line in lines:
#     item = {}
#     item['link'] = line.find_element_by_xpath("./..").get_attribute("href")
#     item['title'] = line.find_element_by_xpath("./font[@class='cont_tit03']").text
#     item['pub_date'] = line.find_element_by_xpath("./font[@class='cont_tit02']").text
#     print(item)
# browser.close()

# # 测试爬取国家统计局 新闻发布会的列表页页面
# browser.get("http://www.stats.gov.cn/tjsj/xwfbh/fbhwd/index_1.html")
# ret = wait.until(EC.presence_of_element_located(
#     (By.XPATH,
#      "//div[@class='center_list']/ul[@class='center_list_contlist']")))   # 等待直到某个元素出现
# # print(ret.tag_name)  # ul
# lines = ret.find_elements_by_xpath("./li/span[@class='cont_tit']//font[@class='cont_tit03']/*")
# # print(lines)
# # print(len(lines))
# """
# <li style="width:590px;">
#     <span class="cont_tit">
#         <img src="../../../images/01.jpg" style="float:left;margin-right:3px;margin-top:3px;">
#             <font class="cont_tit03">
#                 <a href="../../zxfb/201705/t20170515_1494086.html" target="_blank">4月份国民经济继续保持稳中向好态势</a>
#             </font>
#
#             <font class="cont_tit02">
#                 <a href="/tjsj/sjjd/201705/t20170515_1494239.html" class="jieduo" target="_blank"><img src="../../zxfb/201705/W020170515513169544708_r75.jpg" alt="答记者问.jpg"></a>
#             </font>
#     </span>
# </li>
# """
# for line in lines:
#     item = {}
#     link = line.get_attribute("href")
#     # print(link)
#     title = line.text
#     # print(title)
#     item['link'] = link
#     item['title'] = title
#     print(item)
#     print()
#     print()
# browser.close()

# 测试爬取国家统计局 -- 新闻发布会详情页
"""
<font class="xilan_titf">
    <font style="float:left;width:620px;text-align:right;margin-right:60px;">来源：
        <font style="color:#1f5781;margin-right:50px;">国家统计局</font>
        发布时间：2018-05-15&nbsp;10:00
    </font>
    
    <input type="button" value="关闭窗口" onclick="javascript:CloseWebPage()">
    <input type="button" value="打印本页" onclick="javascript:window.print()">
</font>
"""
lst = ['http://www.stats.gov.cn/tjsj/zxfb/200203/t20020328_11504.html',
       'http://www.stats.gov.cn/tjsj/zxfb/200203/t20020328_11479.html']

print(len(lst))
for url in lst:
    browser.get(url)
    try:
        ret = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='TRS_PreAppend']")))
    except:
        try:
            ret = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='TRS_Editor']")))
        except:
            ret = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='center_xilan']")))

    contents = []
    nodes = ret.find_elements_by_xpath("./*")
    for node in nodes:
        if (not node.find_elements_by_xpath(".//table")) and (node.tag_name != 'table'):
            c = node.text
            if c:
                contents.append(c)
        else:
            print("去掉 table 中的内容")
            pass

    ret2 = wait.until(EC.presence_of_element_located(
        # (By.XPATH, "//font[@style='float:left;width:620px;text-align:right;margin-right:60px;']")))
        (By.XPATH, "//font[@class='xilan_titf']")))

    print("\n".join(contents))
    pub_date = datetime.datetime.strptime(re.findall("发布时间：(\d{4}-\d{2}-\d{2})", ret2.text)[0], "%Y-%m-%d")
    print(pub_date)
    print()
    time.sleep(5)
browser.close()
