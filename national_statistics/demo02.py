# 测试获取详情页面 

import time 

import requests as req

from selenium import webdriver 

# 带有表格的详情页 
# url = "http://www.stats.gov.cn/tjsj/zxfb/201910/t20191021_1704063.html"
url = "http://www.stats.gov.cn/tjsj/zxfb/201809/t20180917_1623289.html"

lst = [
    # 'http://www.stats.gov.cn/tjsj/zxfb/202001/t20200109_1721984.html', 'http://www.stats.gov.cn/tjsj/zxfb/202001/t20200109_1721985.html', 'http://www.stats.gov.cn/tjsj/zxfb/202001/t20200106_1721413.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191231_1720657.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191227_1720052.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191224_1719270.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191217_1718007.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717695.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717696.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717697.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717698.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717699.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717656.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191216_1717660.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191211_1716979.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191210_1716702.html', 

# 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191210_1716703.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191209_1716475.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191206_1715827.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191205_1715468.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191204_1715272.html', 
# 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191204_1715262.html', 'http://www.stats.gov.cn/tjsj/zxfb/201912/t20191204_1715246.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191130_1712828.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191127_1712267.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191127_1712037.html', 
# 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191125_1711297.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191122_1710868.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191119_1710335.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191119_1710336.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191119_1710337.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191119_1710338.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191119_1710339.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191119_1710340.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191115_1709560.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191114_1709102.html', 
# 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191114_1709103.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191114_1709104.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191114_1709105.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191114_1709106.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191114_1709083.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191111_1708305.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191109_1708139.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191109_1708140.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191105_1707144.html', 'http://www.stats.gov.cn/tjsj/zxfb/201911/t20191104_1706742.html', 'http://www.stats.gov.cn/tjsj/zxfb/201910/t20191031_1706213.html', 'http://www.stats.gov.cn/tjsj/zxfb/201910/t20191031_1706192.html', 'http://www.stats.gov.cn/tjsj/zxfb/201910/t20191025_1705454.html', 'http://www.stats.gov.cn/tjsj/zxfb/201910/t20191024_1704985.html', 
'http://www.stats.gov.cn/tjsj/zxfb/201910/t20191024_1704994.html']



# ret = req.get(url).text
# print(ret)
# print("CPI环比由涨转平，同比涨幅与上月相同" in ret )


# browser = webdriver.Chrome()
# browser.implicitly_wait(30)  # 隐性等待，最长等30秒
# ret = browser.get(url).source_page
# print(ret)


import requests as req
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

# browser = webdriver.Chrome()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
browser = webdriver.Chrome(desired_capabilities=capa) 
wait = WebDriverWait(browser, 20)  # 等待的最大时间20s

for url in lst: 
    print(url)

    browser.get(url)

    # ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_xilan']")))   # 等待直到某个元素出现
    ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='TRS_PreAppend']")))   # 等待直到某个元素出现
    # print(ret.text)

    contents = []
    nodes = ret.find_elements_by_xpath("./*")

    for node in nodes: 
        if not node.find_elements_by_xpath(".//table"): 
            c = node.text 
            if c: 
                contents.append(c)
        else: 
            print("去掉 table 中的内容 ... ")
            # pass
    # print(contents)
    # print()
    print("\n".join(contents))

    time.sleep(3)
    print()
    print()
    print()

    
browser.close()
