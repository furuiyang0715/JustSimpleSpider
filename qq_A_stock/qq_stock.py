import json
import pprint
import sys
import time
from queue import Queue

import requests
from fake_useragent import UserAgent
from gne import GeneralNewsExtractor

ua = UserAgent()


class qqStock(object):
    def __init__(self):
        self.token = "8f6b50e1667f130c10f981309e1d8200"
        self.headers = ua.random
        self.list_url = "https://pacaio.match.qq.com/irs/rcd?cid=52&token={}" \
       "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&callback=__jp1".format(self.token)
        self.q = Queue()
        self.proxy = None
        self.extractor = GeneralNewsExtractor()

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
            print("获取到的代理是{}".format(proxy))
            ret = requests.get(url, headers={"User-Agent": ua.random}, proxies={"http": proxy})
            return ret

    def _parse_article(self, item):
        vurl = item.get("link")
        body = self._get(vurl).text
        result = self.extractor.extract(body)
        # print(pprint.pformat(result))
        item['article'] = result.get("content")
        item['pub_date'] = result.get("publish_time")
        item['title'] = result.get("title")

        return item

    def _get_list(self):
        while True:
            try:
                list_resp = self._get(self.list_url)
            except:
                self.proxy = None
                time.sleep(3)
            else:
                break

        if list_resp.status_code == 200:
            print("请求列表页成功 ")
            body = list_resp.text
            body = body.lstrip("__jp1(")
            body = body.rstrip(")")
            body = json.loads(body)
            # print(body)
            datas = body.get("data")  # list 数据列表
            # 有两种类型的文章 一种是直接的文章列表页 一种是专题
            specials = []
            articles = []
            for data in datas:
                if data.get("article_type") == 120:
                    specials.append(data)
                elif data.get("article_type") == 0:
                    articles.append(data)
                else:
                    raise Exception("请检查数据")
            for article in articles:
                yield article

            # for special in specials:
            #     # 获取到专题的详情页
            #     special_detail = special.get("vurl")
            #     # print(special_detail)

            # print(specials)
            # print(articles)


            pass
        pass

    def items_gener(self):
        article_gener = self._get_list()
        for article in article_gener:
            # 检查详情页面是否爬取过

            # 创建一个数据对象
            item = {}
            vurl = article.get("vurl")
            item['link'] = vurl
            item = self._parse_article(item)
            yield item

    def start(self):
        for item in self.items_gener():
            # 保存到数据库
            print("{} 已入库".format(item['title']))


if __name__ == "__main__":
    d = qqStock()
    # proxy = d._get_proxy()
    # print(proxy)

    d.start()