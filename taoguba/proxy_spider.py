import time

import requests


class ProxySpider(object):
    """
    与代理相关
    """
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/38.0.2125.122 Safari/537.36',
        'Connection': 'keep-alive',
        'Content-Encoding': 'gzip',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        "referer": "https://www.taoguba.com.cn/quotes/sz300223",
    }

    def get(self, url):
        # 使用 阿布云 代理服务器
        # proxyHost = "http-dyn.abuyun.com"
        proxyHost = "http-cla.abuyun.com"
        # proxyPort = 9020
        proxyPort = 9030
        # 代理隧道验证信息
        # proxyUser = "HI3A82G0357W5O5D"
        proxyUser = "H74JU520TZ0I2SFC"
        # proxyPass = "FEF4967BF6F9BD8A"
        proxyPass = "7F5B56602A1E53B2"
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }

        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        while True:
            resp = requests.get(url, proxies=proxies, headers=self.HEADERS)
            if resp.status_code == 200:
                # print(resp)
                # print(resp.text)
                return resp
            else:
                time.sleep(0.1)

        # # 自建的 ip 代理模块
        # while True:
        #     ip = self.ip_pool.get_one()
        #     print(ip)
        #     proxies = {"http": "http://{}".format(ip)}
        #     ret = requests.get(url, proxies=proxies, headers=self.HEADERS, timeout=3)
        #     if ret.status_code == "200":
        #         return ret
        #     else:
        #         print(ret.status_code)
        #         print("更换 ip")
        #         self.ip_pool.delete_ip(ip)
        #         time.sleep(0.1)
