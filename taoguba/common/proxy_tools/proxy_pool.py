import logging
import random
import string
import time
from collections import deque
from urllib.parse import urlencode

import requests

from requests import Response
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

logger = logging.getLogger()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/38.0.2125.122 Safari/537.36',
    'Connection': 'keep-alive',
    'Content-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}


class GetProxyStrategy(object):
    URL = ''

    def __init__(self):
        self.content = ''

    def execute(self) -> []:
        self.content = self.http_request(self.URL).text

    def http_request(self, url: str, timeout=30) -> Response:
        session = requests.Session()
        session.mount('https://', HTTPAdapter(max_retries=5))
        session.mount('http://', HTTPAdapter(max_retries=5))
        response = session.get(url, headers=HEADERS, timeout=timeout)
        return response


class GetXiciProxyStrategy(GetProxyStrategy):
    SPEED = 100
    NAME = 'Xici'

    def execute(self):
        super(GetXiciProxyStrategy, self).execute()
        ip = []
        soup = BeautifulSoup(self.content, 'html.parser')
        ip_list = soup.find('table', id='ip_list')
        ip_tr_list = ip_list.find_all('tr', limit=101)
        for index, ip_tr in enumerate(ip_tr_list):
            if index == 0:
                continue
            ip_td = ip_tr.find_all('td')
            address = ''
            port = ''
            is_high_quality = True
            for num, data in enumerate(ip_td):
                if num == 1:
                    address = data.getText()
                elif num == 2:
                    port = data.getText()
                elif num == 6 or num == 7:
                    try:
                        value = data.find('div', class_='bar').find('div').attrs['style']  # type:str
                        is_high_quality = (
                                is_high_quality and
                                int(value.replace('width:', '').replace('%', '')) > self.SPEED)
                    except:
                        break
                elif num > 7:
                    break
            if is_high_quality:
                ip.append(address + ':' + port)
        return ip


class GetXiciChinaProxyStrategy(GetXiciProxyStrategy):
    URL = 'http://www.xicidaili.com/nn/'
    SPEED = 85


class GetXiciForeignProxyStrategy(GetXiciProxyStrategy):
    URL = 'http://www.xicidaili.com/wn/'
    SPEED = 80


class Get66ipProxyStrategy(GetProxyStrategy):
    NAME = '66ip'
    URL = 'http://www.66ip.cn/nmtq.php?getnum=800&isp=0&anonymoustype=4&start=&\
    ports=&export=&ipaddress=&area=1&proxytype=0&api=66ip'

    def execute(self):
        super(Get66ipProxyStrategy, self).execute()
        soup = BeautifulSoup(self.content, 'html.parser')
        ip = []
        for br in soup.findAll('br'):
            ip.append(br.next.strip())
        return ip


class KDLAPIProxyStrategy(GetProxyStrategy):
    NAME = "KDLAPI"
    URL = "http://ent.kdlapi.com/api/getproxy/?orderid=924829619838717&num=100&protocol=1&method=2&an_an=1&an_ha=1&sep=1"

    def execute(self):
        proxy_list = requests.get(self.URL, timeout=20).text.split("\r\n")
        return proxy_list


class PrivateProxyStrategy(GetProxyStrategy):
    NAME = "PRIVATEKDLAPI"
    # URL = PRIVATE_PROXY_URL

    def execute(self):
        proxy_list = requests.get(self.URL, timeout=1).text.split("\r\n")
        logger.info(f"更新私有代理池 pool: {proxy_list}")
        return proxy_list


class GetKuaidailiProxyStrategy(GetProxyStrategy):
    NAME = 'Kuaidaili'
    URL = 'http://www.kuaidaili.com/free/inha/%s/'
    SPEED = 5

    def execute(self):
        ip = []
        for num in range(1, 10):
            url = self.URL % num
            context = self.http_request(url).text
            ip = ip + self.parse(context)
            time.sleep(3)
        return ip

    def parse(self, content) -> []:
        ip = []
        soup = BeautifulSoup(content, 'html.parser')
        ip_table = soup.find('tbody')
        ip_tr_list = ip_table.find_all('tr')
        for ip_tr in ip_tr_list:
            ip_td = ip_tr.find_all('td')
            address = ''
            port = ''
            is_high_quality = True
            for num, data in enumerate(ip_td):
                if num == 0:
                    address = data.getText()
                elif num == 1:
                    port = data.getText()
                elif num == 2:
                    is_high_quality = data.getText() == '高匿名'
                    if not is_high_quality:
                        break
                elif num == 6:
                    try:
                        is_high_quality = (is_high_quality
                                           and float(data.getText()[:-1]) < self.SPEED)
                        break
                    except:
                        break
            if is_high_quality:
                ip.append(address + ':' + port)
        return ip


def crawl_proxy() -> []:
    proxy_list = []

    def get_proxy_list(_strategy):
        _proxy_list = []
        _ip_list = _strategy.execute()
        # print(_ip_list)
        for ip in _ip_list:
            if ip.strip() == '':
                continue
            _proxy = ip
            # _proxy = Proxy.create(ip, _strategy.NAME)
            # _proxy = Proxy(ip)
            _proxy_list.append(_proxy)
        return _proxy_list

    # 根据环境变量确定使用哪个代理 私有代理仅仅在服务器上可以使用
    proxy_list += get_proxy_list(KDLAPIProxyStrategy())

    # 以下略去 ......
    # proxy_list += get_proxy_list(PrivateProxyStrategy())
    # proxy_list += get_proxy_list(GetKuaidailiProxyStrategy())
    # proxy_list += get_proxy_list(Get66ipProxyStrategy())
    # proxy_list += get_proxy_list(GetXiciChinaProxyStrategy())
    # proxy_list += get_proxy_list(GetXiciForeignProxyStrategy())
    # return proxy_list
    return proxy_list


def make_query_params():
    """
    拼接动态请求参数
    """
    query_params = {
        'type': '8224',
        'pageindex': str(1),
        'pagesize': str(10),
        'keyword': "格力电器".encode(),
        'name': 'caifuhaowenzhang',
        'cb': 'jQuery{}_{}'.format(
            ''.join(random.choice(string.digits) for i in range(0, 21)),
            str(int(time.time() * 1000))
        ),
        '_': str(int(time.time() * 1000)),
    }
    return query_params


def check_ip(ip):
    list_url = "http://api.so.eastmoney.com/bussiness/Web/GetSearchList?"
    query_params = make_query_params()
    start_url = list_url + urlencode(query_params)
    proxy_settings = {"https": "https://{}".format(ip)}
    # proxy_settings = {"http": "http://{}".format(ip)}

    detail = "http://caifuhao.eastmoney.com/news/20191224170753889118840"
    try:
        # ret = requests.get(start_url, proxies=proxy_settings, timeout=0.5).status_code
        ret = requests.get(detail, proxies=proxy_settings, timeout=0.5)
    except Exception as e:
        # print(e)
        return False
    else:
        if ret.status_code == 200:
            # print(ret.text)
            return True
        else:
            print(ret.status_code)
            return False


class BaseProxyPool(object):

    # Singleton
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            org = super(BaseProxyPool, cls)
            cls._instance = org.__new__(cls, *args)
        return cls._instance

    def crawl_proxy_task(self):
        proxy_list = crawl_proxy()
        return proxy_list

    def ping_ip(self, ip, url="http://caifuhao.eastmoney.com/news/20191106065250079316840"):
        proxy_settings = {"http": "http://{}".format(ip)}
        try:
            requests.get(url, proxies=proxy_settings, timeout=0.5)
        except:
            return False
        else:
            return True


class QueueProxyPool(BaseProxyPool):
    def __init__(self):
        self.pool = self.get_pool()

    def get_pool(self):
        pool = deque()
        return pool

    def drop_proxy(self):
        self.pool.clear()

    def save_proxy(self, proxy_list: list):
        if not isinstance(proxy_list, list):
            proxy_list = [proxy_list]
        self.pool.extend(proxy_list)

    def delete_ip(self, ip: str):
        #  http://113.121.64.57:9999
        if ip.startswith("http"):
            ip = ip.split("://")[1]
        try:
            self.pool.remove(ip)
        except:
            pass
        logger.info(f"删除了ip {ip}")

    def show_proxy(self):
        return self.pool.copy()

    def get_one(self):
        ip = None
        while not ip:
            # with Lock:
            try:
                # ip = self.pool.pop()
                ip = random.choice(list(self.pool))
            except:
                pass

            if len(list(self.pool)) < 5:
                proxys = self.crawl_proxy_task()
                self.save_proxy(proxys)
        return ip


if __name__ == "__main__":
    # nt = lambda: time.time()
    # t1 = nt()
    # lst = crawl_proxy()
    # print(lst)
    # print(len(lst))
    # print(nt() - t1)
    # for p in lst:
    #     print(check_ip(p))

    q = QueueProxyPool()
    print(q.get_one())
