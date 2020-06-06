from selenium import webdriver
import time

from configs import WEIBO_PASSWORD


def weibo_login(username, password):
    browser = webdriver.Chrome()
    # 打开微博登录页
    browser.get('https://passport.weibo.cn/signin/login')
    browser.implicitly_wait(5)
    time.sleep(1)
    # 填写登录信息:用户名、密码
    browser.find_element_by_id("loginName").send_keys(username)
    browser.find_element_by_id("loginPassword").send_keys(password)
    time.sleep(1)
    # 点击登录
    browser.find_element_by_id("loginAction").click()
    time.sleep(10)


# 设置用户名、密码
username = '15626046299'
password = WEIBO_PASSWORD
print(password)
# weibo_login(username, password)

