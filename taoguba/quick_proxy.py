# 定义快速爬取模块
import traceback

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()


class QuickProxy(object):
    current_proxy = None

    def quick_fectch(self, url):
        purl = "http://www.xicidaili.com/nn/"
        web_html = requests.get(purl, headers={"User-Agent": ua.random}).text
        soup = BeautifulSoup(web_html, 'lxml')
        ip_list = soup.find(id='ip_list').find_all('tr')
        for ip_info in ip_list:
            td_list = ip_info.find_all('td')
            if len(td_list) > 0:
                ip_address = td_list[1].text
                ip_port = td_list[2].text
                proxy = ip_address + ":" + ip_port
                header = {'User-Agent': ua.random}
                proxies = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}
                try:
                    r = requests.get(url, headers=header,
                                     proxies=proxies, timeout=3)
                except:
                    print('fail-{}'.format(proxy))
                else:
                    print('success-{}'.format(proxy))
                    self.current_proxy = proxy
                    return True, r
        return False, None

    def get(self, url):
        """
        对外暴露端口
        :param url:  请求的 url
        :return:
        """
        if self.current_proxy:
            try:
                response = requests.get(url, headers={"User-Agent": ua.random},
                                        proxies={"http": "http://{}".format(self.current_proxy)},
                                        timeout=3
                                        )
            except:
                traceback.print_exc()
                print("上一次的代理已经失效")
            else:
                print("成功")
                return response

        ret, response = False, None
        while not ret:
            print("开始新一轮的爬取 ")
            ret, response = self.quick_fectch(url)
        return response


# d = QuickProxy()
# d.get("https://www.taoguba.com.cn/quotes/sz300223")
# d.get("https://www.taoguba.com.cn/Article/2672273/1")
# # print(d.current_proxy)