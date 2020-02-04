# 测试获取列表页面
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
browser = webdriver.Chrome(desired_capabilities=capa)  # 关键!记得添加
wait = WebDriverWait(browser, 20)  # 等待的最大时间20s



browser.get("http://www.stats.gov.cn/tjsj/zxfb/")
ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_list']/ul[@class='center_list_contlist']")))   # 等待直到某个元素出现

print(ret.tag_name)  # ul
lines = ret.find_elements_by_xpath("./li/a/*")
for line in lines: 
    item = {}
    item['link'] = line.find_element_by_xpath("./..").get_attribute("href")
    item['title'] = line.find_element_by_xpath("./font[@class='cont_tit03']").text
    item['pub_date'] = line.find_element_by_xpath("./font[@class='cont_tit02']").text

    print(item)
    
browser.close()




