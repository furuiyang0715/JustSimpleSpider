import re
import time

import requests
import json


class DoubanTvSpider:
    """爬取豆瓣上的全部电视剧信息
    https://m.douban.com/rexxar/api/v2/subject_collection/tv_american/items?os=ios&for_mobile=1&callback=jsonp1&start=0&count=18&loc_id=108288&_=1593661618578

    """
    def __init__(self):
        self.tv_urls = [
            {
              "country": "US",
              "Referer": "https://m.douban.com/tv/american",
              "url": "https://m.douban.com/rexxar/api/v2/subject_collection/filter_tv_american_hot/items?start={}&count=18&loc_id=108288"
            },
            {
                "country": "EN",
                "Referer": "https://m.douban.com/tv/british",
                "url": "https://m.douban.com/rexxar/api/v2/subject_collection/filter_tv_english_hot/items?start={}&count=18&loc_id=108288"
            },
            {
                "country": "ZH",
                "Referer": "https://m.douban.com/tv/chinese",
                "url": "https://m.douban.com/rexxar/api/v2/subject_collection/filter_tv_domestic_hot/items?start={}&count=18&loc_id=108288"
            }
        ]

        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
        }

    def get_page_from_url(self, url, referer):
        self.headers["Referer"] = referer
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.content.decode()

    def get_tvitem_list(self, page):
        dic = json.loads(page)
        return dic["subject_collection_items"], dic["total"]

    def save_tv_list(self, tv_list, country):
        with open("douban_tv.txt", "a", encoding="UTF-8") as f:
            for tv in tv_list:
                tv["country"] = country
                json.dump(tv, f, ensure_ascii=False)
                f.write("\n")

    def run(self):
        for tv_url in self.tv_urls:
            # 定义变量,用于记录开始编号
            num = 0
            total = 100  # 为了能让循环进来
            while num < total:
                    # 构造起始页 URL
                    url = tv_url["url"].format(num)
                    # 发送请求获取数据
                    page = self.get_page_from_url(url, tv_url["Referer"])
                    if not page:
                        return
                    # 移动代码快捷键: alt + shift + 上下箭头
                    # print(page)
                    # 解析数据,获取电视剧信息列表
                    tv_list, total = self.get_tvitem_list(page)
                    print(tv_list, total)
                    # 把电视剧信息列表,存储文件中,每一个电视剧信息存储一行
                    # self.save_tv_list(tv_list, tv_url["country"])
                    # 方式1: 如果这一页不够18条就结束
                    # if len(tv_list) < 18:
                    #     break
                    # 构造下一页的URL
                    num += 18


def task():
    headers = {
        "Referer": "https://m.douban.com/tv/american",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
    }
    url = 'https://m.douban.com/rexxar/api/v2/subject_collection/tv_american/items?os=ios&for_mobile=1&callback=jsonp1&start=0&count=18&loc_id=108288&_={}'.format(int(time.time()*1000))
    resp = requests.get(url, headers=headers)
    print(resp)
    if resp.status_code == 200:
        text = resp.text
        _text = re.findall(";jsonp1\((.*)\)", text)[0]
        datas = json.loads(_text)
        print(datas)

    pass


if __name__ == '__main__':
    # dts = DoubanTvSpider()
    # dts.run()

    task()
