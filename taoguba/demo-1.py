#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/11/22
# @Author  : liangk
# @Site    :
# @File    : auto_archive_ios.py
# @Software: PyCharm

import random
import sys

import requests
from bs4 import BeautifulSoup
import json


class GetIp(object):
    """抓取代理IP"""

    def __init__(self):
        """初始化变量"""
        self.url = 'http://www.xicidaili.com/nn/'
        self.check_url = 'https://www.ip.cn/'
        self.ip_list = []

    def kuai_proxy(self):
        """
        爬取的开放代理
        :return:
        """
        url = "http://ent.kdlapi.com/api/getproxy/?orderid=924829619838717&num=100&protocol=1&method=2&an_an=1&an_ha=1&sep=1"
        proxies = requests.get(url).text.split("\r\n")
        print(proxies)
        return proxies

    @staticmethod
    def get_html(url):
        """请求html页面信息"""
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        try:
            request = requests.get(url=url, headers=header)
            request.encoding = 'utf-8'
            html = request.text
            return html
        except Exception as e:
            return ''

    def get_available_ip(self, ip_address, ip_port):
        """检测IP地址是否可用"""
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        ip_url_next = '://' + ip_address + ':' + ip_port
        proxies = {'http': 'http' + ip_url_next, 'https': 'https' + ip_url_next}
        try:
            r = requests.get(self.check_url, headers=header, proxies=proxies, timeout=3)
            html = r.text
        except:
            print('fail-%s' % ip_address)
        else:
            print('success-%s' % ip_address)
            soup = BeautifulSoup(html, 'lxml')
            div = soup.find(class_='well')
            if div:
                print(div.text)
            ip_info = {'address': ip_address, 'port': ip_port}
            self.ip_list.append(ip_info)

    def main(self):
        """主方法"""
        web_html = self.get_html(self.url)
        soup = BeautifulSoup(web_html, 'lxml')
        ip_list = soup.find(id='ip_list').find_all('tr')
        for ip_info in ip_list:
            td_list = ip_info.find_all('td')
            if len(td_list) > 0:
                ip_address = td_list[1].text
                ip_port = td_list[2].text
                # 检测IP地址是否有效
                self.get_available_ip(ip_address, ip_port)
        # 写入有效文件
        with open('ip.txt', 'w') as file:
            json.dump(self.ip_list, file)
        print(self.ip_list)

    def get_proxie(self, random_number):
        with open('ip.txt', 'r') as file:
        # with open('nip.txt', 'r') as file:
            ip_list = json.load(file)
            if random_number == -1:
                random_number = random.randint(0, len(ip_list) - 1)
            ip_info = ip_list[random_number]
            ip_url_next = '://' + ip_info['address'] + ':' + ip_info['port']
            proxies = {'http': 'http' + ip_url_next, 'https': 'https' + ip_url_next}
            return random_number, proxies


# 程序主入口
if __name__ == '__main__':
    get_ip = GetIp()

    # lst = get_ip.kuai_proxy()
    # for p in lst:
    #     host, ip = p.split(":")
    #     get_ip.get_available_ip(host, ip)
    # print(get_ip.ip_list)
    # with open('nip.txt', 'w') as file:
    #     json.dump(get_ip.ip_list, file)

    # sys.exit(0)


    get_ip.main()

    for i in range(2):
        _, proxy = get_ip.get_proxie(i)
        print(proxy)
        try:
            ret = requests.get("https://www.taoguba.com.cn/quotes/sz300223", proxies=proxy, timeout=10)
            print(ret)
        except:
            print("pass")

