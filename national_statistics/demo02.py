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





ret = gen_uhit_items(ll)
print(pprint.pformat(ret))
