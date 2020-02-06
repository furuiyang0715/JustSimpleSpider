import json
import pprint
import time

import requests
from bs4 import BeautifulSoup


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
    }

    def _proxy_get(self, url, proxies):
        """
        使用某种生成的代理去访问
        :param url:
        :param proxies:
        :return:
        """
        while True:
            if proxies:
                proxy = proxies[-1]
                proxy = {"http": "http://" + proxy}
                try:
                    ret = requests.get(url, proxies=proxy, headers=self.HEADERS,
                                       timeout=1
                                       )
                except:
                    print("连接超时 {}".format(proxies.pop()))
                else:
                    if ret.status_code == 200:
                        return ret
                    else:
                        ret2 = requests.get("https://www.douban.com/", proxies=proxy, headers=self.HEADERS, timeout=1)
                        # ret2 = requests.get("https://www.taoguba.com.cn/quotes/sz300223", proxies=proxy, headers=self.HEADERS, timeout=3)
                        print("访问测试网站的结果 {}".format(ret2))
                        print('因为{} 删除{}'.format(ret.status_code, proxies.pop()))
                        time.sleep(0.1)
            else:
                print("需要重新爬取一批代理")

    def sm_proxy(self):
        """
        线上的私密代理 (高匿)
        :return:
        """
        url = 'https://dps.kdlapi.com/api/getdps/?orderid=934751511166930&num=20&pt=1&sep=1'
        proxies = requests.get(url).text.split("\r\n")
        # print(proxies)   # ['119.102.8.221:23460', '182.34.34.85:19322'
        return proxies

    def kuai_proxy(self):
        """
        爬取的开放代理
        :return:
        """
        url = "http://ent.kdlapi.com/api/getproxy/?orderid=924829619838717&num=100&protocol=1&method=2&an_an=1&an_ha=1&sep=1"
        proxies = requests.get(url).text.split("\r\n")
        print(proxies)
        return proxies
        # base_url = 'https://www.kuaidaili.com/free/inha/{}/'
        # for i in range(1, 5):
        #     time.sleep(1)
        #     res = requests.get(base_url.format(i),
        #                        headers=self.HEADERS,
        #                        )
        #     soup = BeautifulSoup(res.text, 'lxml')
        #     trs = soup.find_all('tr')
        #     for tr in trs[1:]:
        #         tds = tr.find_all('td')
        #         # lst.append({str(tds[3].text).lower(): str(tds[0].text) + ':' + str(tds[1].text)})
        #         lst.append(str(tds[0].text) + ':' + str(tds[1].text))
        #     # print(lst)
        #     return lst

    def kuai_get(self, url):
        """
        使用自己爬取的开放快代理去访问
        :param url:
        :return:
        """
        proxies = self.kuai_proxy()
        # ['110.243.2.57:9999', '60.167.82.55:9999',
        return self._proxy_get(url, proxies)

    def sm_get(self, url):
        """
        私密代理访问 仅限于线上使用
        :param url:
        :return:
        """
        proxies = self.sm_proxy()
        # ['183.164.238.250:22628', '125.112.175.205:19861'
        return self._proxy_get(url, proxies)

    def abu_get(self, url):
        """使用阿布云代理"""
        proxyHost = "http-cla.abuyun.com"
        proxyPort = 9030
        # 代理隧道验证信息
        proxyUser = "H74JU520TZ0I2SFC"
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
            resp = requests.get(url,
                                proxies=proxies,
                                headers=self.HEADERS,
                                timeout=3,
                                )
            if resp.status_code == 200:
                return resp
            else:
                time.sleep(0.1)

    def get(self, url):
        # 不使用代理
        # return requests.get(url)

        # 使用阿布云代理
        # return self.abu_get(url)

        # 开放快代理(两种)
        return self.kuai_get(url)

        # 线上私密代理访问
        # return self.sm_get(url)


if __name__ == "__main__":
    d = ProxySpider()

    # ret = d.get("https://www.taoguba.com.cn/Article/2672273/1")
    ret = d.get("https://www.taoguba.com.cn/quotes/sz300223")
    # ret = d.get("https://blog.csdn.net/Enjolras_fuu/article/details/104175487")
    # ret = d.get("http://httpbin.org/headers")
    # ret = d.get("http://httpbin.org/ip")
    # ret = d.get("https://github.com/binux/pyspider/blob/master/pyspider/message_queue/redis_queue.py")

    print("=======")
    print(ret.text)



"""
{
  "origin": "119.130.70.97"
}
"""