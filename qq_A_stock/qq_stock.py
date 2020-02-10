from queue import Queue

import requests
from fake_useragent import UserAgent

ua = UserAgent()


class qqStock(object):
    def __init__(self):
        self.token = "8f6b50e1667f130c10f981309e1d8200"
        self.headers = ua.random
        self.list_url = "https://pacaio.match.qq.com/irs/rcd?cid=52&token={}" \
       "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&callback=__jp1".format(self.token)
        self.q = Queue()
        self.proxy = None

    def update_proxies(self):
        # run()
        with open("proxies.txt", "r") as f:
            proxies = f.readlines()
        proxies = [p.strip() for p in proxies]
        for proxy in proxies:
            self.q.put(proxy)

        # 将代理一一添加到爬虫的队列存储对象中
        # print(proxies)
        # print(type(proxies))
        # self.proxies = [p.strip() for p in proxies]
        # print(self.proxies)

    def _get_proxy(self):
        if self.proxy:
            return self.proxy

        elif not self.q.empty():
            self.proxy = self.q.get()
            return self.proxy

        else:
            self.update_proxies()
            self.proxy = self.q.get()
            return self.proxy

    def _get(self, url):
            proxy = self._get_proxy()
            ret = requests.get(url, headers={"User-Agent": ua.random}, proxies={"http": proxy})
            return ret

    def start(self):
        ret = self._get(self.list_url)
        return ret


if __name__ == "__main__":
    d = qqStock()
    # proxy = d._get_proxy()
    # print(proxy)

    ret = d.start()
    print(ret)