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
wait = WebDriverWait(browser, 20)  # 等待的最大时间20s


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
lst = ['http://www.stats.gov.cn/tjsj/zxfb/201304/t20130415_12960.html',
       'http://www.stats.gov.cn/tjsj/zxfb/201301/t20130118_12924.html',
       'http://www.stats.gov.cn/tjsj/zxfb/201210/t20121018_12887.html',
       'http://www.stats.gov.cn/tjsj/zxfb/201207/t20120713_12847.html',
       'http://www.stats.gov.cn/tjsj/zxfb/201204/t20120413_12808.html',
       'http://www.stats.gov.cn/tjsj/zxfb/201201/t20120117_12777.html',
       'http://www.stats.gov.cn/tjsj/zxfb/201110/t20111018_12749.html', 'http://www.stats.gov.cn/tjsj/zxfb/201107/t20110713_12725.html', 'http://www.stats.gov.cn/tjsj/zxfb/201104/t20110415_12702.html', 'http://www.stats.gov.cn/tjsj/zxfb/201101/t20110120_12689.html', 'http://www.stats.gov.cn/tjsj/zxfb/201010/t20101021_12675.html', 'http://www.stats.gov.cn/tjsj/zxfb/201007/t20100715_12658.html', 'http://www.stats.gov.cn/tjsj/zxfb/201004/t20100415_12646.html', 'http://www.stats.gov.cn/tjsj/zxfb/201001/t20100121_12629.html', 'http://www.stats.gov.cn/tjsj/zxfb/200910/t20091022_12613.html', 'http://www.stats.gov.cn/tjsj/zxfb/200907/t20090716_12586.html', 'http://www.stats.gov.cn/tjsj/zxfb/200904/t20090416_12553.html', 'http://www.stats.gov.cn/tjsj/zxfb/200901/t20090122_12538.html', 'http://www.stats.gov.cn/tjsj/zxfb/200810/t20081020_12507.html', 'http://www.stats.gov.cn/tjsj/zxfb/200807/t20080717_12476.html', 'http://www.stats.gov.cn/tjsj/zxfb/200804/t20080416_12445.html', 'http://www.stats.gov.cn/tjsj/zxfb/200801/t20080124_12431.html', 'http://www.stats.gov.cn/tjsj/zxfb/200710/t20071025_12402.html', 'http://www.stats.gov.cn/tjsj/zxfb/200707/t20070719_12372.html', 'http://www.stats.gov.cn/tjsj/zxfb/200704/t20070419_12342.html', 'http://www.stats.gov.cn/tjsj/zxfb/200701/t20070125_12329.html', 'http://www.stats.gov.cn/tjsj/zxfb/200610/t20061019_12293.html', 'http://www.stats.gov.cn/tjsj/zxfb/200607/t20060718_12248.html', 'http://www.stats.gov.cn/tjsj/zxfb/200604/t20060420_12208.html', 'http://www.stats.gov.cn/tjsj/zxfb/200601/t20060125_12185.html', 'http://www.stats.gov.cn/tjsj/zxfb/200510/t20051020_12137.html', 'http://www.stats.gov.cn/tjsj/zxfb/200507/t20050720_12093.html', 'http://www.stats.gov.cn/tjsj/zxfb/200504/t20050420_12042.html', 'http://www.stats.gov.cn/tjsj/zxfb/200501/t20050125_12014.html', 'http://www.stats.gov.cn/tjsj/zxfb/200410/t20041022_11970.html', 'http://www.stats.gov.cn/tjsj/zxfb/200407/t20040716_11916.html', 'http://www.stats.gov.cn/tjsj/zxfb/200404/t20040415_11853.html', 'http://www.stats.gov.cn/tjsj/zxfb/200310/t20031017_11771.html', 'http://www.stats.gov.cn/tjsj/zxfb/200307/t20030717_11716.html', 'http://www.stats.gov.cn/tjsj/zxfb/200304/t20030417_11687.html', 'http://www.stats.gov.cn/tjsj/zxfb/200210/t20021016_11635.html', 'http://www.stats.gov.cn/tjsj/zxfb/200207/t20020715_11605.html', 'http://www.stats.gov.cn/tjsj/zxfb/200204/t20020417_11558.html', 'http://www.stats.gov.cn/tjsj/zxfb/200203/t20020328_11527.html', 'http://www.stats.gov.cn/tjsj/zxfb/200203/t20020328_11504.html', 'http://www.stats.gov.cn/tjsj/zxfb/200203/t20020328_11479.html']
print(len(lst))
for url in lst:
    browser.get(url)
    try:
        ret = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='TRS_PreAppend']")))
    except selenium.common.exceptions.TimeoutException:
        ret = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='TRS_Editor']")))
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
    time.sleep(10)
browser.close()
