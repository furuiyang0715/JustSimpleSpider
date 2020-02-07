import json
import pprint
import random
import sys
import time
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


ua = UserAgent()


class ProxySpider(object):
    def abu_get(self, url):
        """使用阿布云代理 默认失败后重新发起请求"""
        proxy_host = "http-cla.abuyun.com"
        proxy_port = 9030
        # 代理隧道验证信息
        proxy_user = "H74JU520TZ0I2SFC"
        proxy_pass = "7F5B56602A1E53B2"
        proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxy_host,
            "port": proxy_port,
            "user": proxy_user,
            "pass": proxy_pass,
        }
        proxies = {
            "http": proxy_meta,
            "https": proxy_meta,
        }
        retry = 3
        while True:
            try:
                resp = requests.get(url,
                                    proxies=proxies,
                                    headers={"User-Agent": ua.random},
                                    timeout=3,
                                    )
                if resp.status_code == 200:
                    return True
                else:
                    retry -= 1
                    time.sleep(1)
                    if retry <= 0:
                        break
            except:
                retry -= 1
                time.sleep(1)
                if retry <= 0:
                    break
        return False

    def _get(self, url: str, proxy: str):
        """
        底层委托给 requests 库访问
        :param url:
        :param proxy: host:port 格式
        :return:
        """
        retry = 3
        while True:
            try:
                resp = requests.get(url,
                                    proxies={"http": "http://{}".format(proxy)},
                                    headers={"User-Agent": ua.random},
                                    timeout=3,
                                    )
                if resp.status_code == 200:
                    return True
                else:
                    retry -= 1
                    time.sleep(1)
                    if retry <= 0:
                        break
            except:
                retry -= 1
                time.sleep(1)
                if retry <= 0:
                    break
        return False

    def _safe_proxy(self, proxy):
        """
        规范从不同的代理源获取的代理字符串的格式
        :param proxy:
        :return: proxy: host:port 格式
        """

    def _crawl_from(self, origin: str):
        """
        根据 origin 字段判断爬取源 获取规范化之后的代理
        :param origin:
        :return:
        """
        if origin == "OPEN_KUAI":
            url = "http://ent.kdlapi.com/api/getproxy/?orderid=924829619838717&num=20&protocol=1&method=2&an_an=1&an_ha=1&sep=1"
            proxies = requests.get(url).text.split("\r\n")
            return proxies
        elif origin == "PRIVATE_KUAI":
            url = 'https://dps.kdlapi.com/api/getdps/?orderid=934751511166930&num=20&pt=1&sep=1'
            proxies = requests.get(url).text.split("\r\n")
            return proxies
        elif origin == "FREE_KUAI":
            proxies = []
            url = 'https://www.kuaidaili.com/free/inha/{}/'
            for i in range(1, 20):
                res = requests.get(url.format(i), headers={"User-Agent": ua.random})
                soup = BeautifulSoup(res.text, 'lxml')
                trs = soup.find_all('tr')
                for tr in trs[1:]:
                    tds = tr.find_all('td')
                proxies.append(str(tds[0].text) + ':' + str(tds[1].text))
            return proxies
        elif origin == "XICIDAILI":
            proxies = []
            url = "http://www.xicidaili.com/nn/"
            web_html = requests.get(url, headers={"User-Agent": ua.random}).text
            soup = BeautifulSoup(web_html, 'lxml')
            ip_list = soup.find(id='ip_list').find_all('tr')
            for ip_info in ip_list:
                td_list = ip_info.find_all('td')
                if len(td_list) > 0:
                    ip_address = td_list[1].text
                    ip_port = td_list[2].text
                    proxies.append(ip_address+":"+ip_port)
            return proxies

    def _check_available_ip(self, proxy):
        """检测IP地址是否可用"""
        header = {'User-Agent': ua.random}
        proxies = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}
        try:
            r = requests.get("http://httpbin.org/ip", headers=header, proxies=proxies, timeout=3)
            # html = r.text
        except:
            print('fail-{}'.format(proxy))
            return False
        else:
            print('success-{}'.format(proxy))
            return True
            # soup = BeautifulSoup(html, 'lxml')
            # div = soup.find(class_='well')
            # if div:
            #     print(div.text)
            # ip_info = {'address': ip_address, 'port': ip_port}
            # self.ip_list.append(ip_info)

    def _save_to_file(self, ip_list):
        """将可用 ip 存入文件中"""
        print("保存可用 ip")
        with open('ip.txt', 'w') as file:
            json.dump(ip_list, file)

    def save(self, proxies):
        ip_list = []
        for proxy in proxies:
            if self._check_available_ip(proxy):
                ip_list.append(proxy)
        if ip_list:
            self._save_to_file(ip_list)

    def get_proxy(self, random_number):
        with open('ip.txt', 'r') as file:
            ip_list = json.load(file)
            if random_number == -1:
                random_number = random.randint(0, len(ip_list) - 1)
            proxy = ip_list[random_number]
            return proxy

    def get(self, url):
        """
        对外暴露端口
        :param url:  请求的 url
        :return:
        """

        # return requests.get(url)

        # 使用阿布云代理
        # return self.abu_get(url)

        # 开放快代理(两种)
        # proxies = self._crawl_from("OPEN_KUAI")
        # proxies = self._crawl_from("PRIVATE_KUAI")
        # proxies = self._crawl_from("FREE_KUAI")
        proxies = self._crawl_from("XICIDAILI")
        # print(proxies)
        # self.save(proxies)
        proxy = self.get_proxy(1)
        print(proxy)
        return self._get(url, proxy)


if __name__ == "__main__":
    d = ProxySpider()
    # demo_url = "https://www.taoguba.com.cn/quotes/sz300223"
    # demo_url = "https://www.taoguba.com.cn/Article/2672273/1"
    demo_url = "https://blog.csdn.net/Enjolras_fuu/article/details/104175487"
    ret = d.get(demo_url)
    print(ret)