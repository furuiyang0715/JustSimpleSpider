# -*- coding: utf-8 -*-
import datetime
import json
import pprint
import random
import re
import time

from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from lxml import html

from base import SpiderBase


class Taoguba(SpiderBase):
    def __init__(self, name, code):
        super(Taoguba, self).__init__()
        self.headers.update({
            'referer': 'https://www.taoguba.com.cn/quotes/sz000651',
            'cookie': '''JSESSIONID=f45d82d9-8811-46e2-ad9d-b51966a460cc; Hm_lvt_cc6a63a887a7d811c92b7cc41c441837=1594448378; UM_distinctid=1733c8778dd26a-07b2c169f81009-31617402-1fa400-1733c8778dea53; CNZZDATA1574657=cnzz_eid%3D512829114-1594445650-%26ntime%3D1594445650; __gads=ID=35d9e7fe87d53615:T=1594448473:S=ALNI_MYwpLq-g-JJX1Wc5jpH6fLV_w04wg; Hm_lpvt_cc6a63a887a7d811c92b7cc41c441837=1594448701'''
        })
        print(pprint.pformat(self.headers))
        self.name = name
        # 最新接口
        self.refresh_url = 'https://www.taoguba.com.cn/quotes/getStockUpToDate?'    # 旧版接口
        # 最热接口
        # self.refresh_url = 'https://www.taoguba.com.cn/quotes/getStockHeat?'        # 新版接口

        self.page_num = 20
        self.code = code
        self.table_name = 'taoguba'
        self.fields = [
            'pub_date',
            'code',
            'chinameabbr',    # 股票中文简称
            'stockattr',      # 相关个股
            'title',
            'link',
            'article',
        ]

    def get(self, url):
        resp = requests.get(url, headers=self.headers, timeout=3)
        return resp

    @staticmethod
    def convert_dt(time_stamp):
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d

    def make_query_params(self, timestamp):
        query_params = {
            'stockCode': self.code,  # 查询股票代码
            'actionDate': timestamp,  # 只会按照数量返回这个时间戳之前(即更早)的数据
            'perPageNum': self.page_num,  # 每次请求返回的个数
            "isOpen": "false",
        }
        return query_params

    def _parse_page(self, body):
        """
        对文章详情页面进行解析
        """
        s_html = re.findall(r"<!-- 主贴内容开始 -->(.*?)<!-- 主贴内容结束 -->", body, re.S | re.M)[0]
        soup = BeautifulSoup(s_html, 'lxml')
        # 因为是要求文章中的图片被替换为链接放在相对应的位置所以这样子搞了w(ﾟДﾟ)w 之后看看有啥更好的办法
        imgs = soup.find_all(attrs={'data-type': 'contentImage'})
        if imgs:
            urls = [img['data-original'] for img in imgs]
            s_imgs = re.findall(r"<img.*?/>", s_html)  # 非贪婪匹配
            match_info = dict(zip(s_imgs, urls))
            for s_img in s_imgs:
                s_html = s_html.replace(s_img, match_info.get(s_img))
            # 替换之后再重新构建一次 这时候用 text 就直接拿到了 url ^_^
            soup = BeautifulSoup(s_html, 'lxml')
        text = soup.div.text.strip()
        return text

    def _parse_page_num(self, body):
        """
        判断当前的文章详情页文章一共分几页
        :param page:
        :return:
        """
        doc = html.fromstring(body)
        page_num = doc.xpath("//div[@class='t_page right fy_pd3']/div[@class='left t_page01']")
        page_str = page_num[0].text_content()  # 末页下一页上一页首页共1/1页
        page_now, page_all = re.findall("共(.+)/(.+)页", page_str)[0]
        return page_now, page_all

    def parse_detail(self, body, rid):
        try:
            return self._parse_detail(body, rid)
        except Exception as e:
            print("详情页解析失败>> {}".format(e))
            return None

    def _parse_detail(self, body, rid):
        page_now, page_all = self._parse_page_num(body)
        print(page_now, page_all)
        # 文章仅一页
        if page_all == "1" and page_now == page_all:
            print("文章仅一页")
            content = self._parse_page(body)
            print(f"已经获取到当前页面的内容>>  {content[:10]}")
            return content

        # 一次爬取每一页再拼接起来
        else:
            content_dict = {}
            while int(page_now) <= int(page_all):
                print(f"开始爬取文章的第 {page_now} / {page_all} 页")
                url = "https://www.taoguba.com.cn/Article/" + str(rid) + "/" + page_now
                content_dict[page_now] = self._parse_page(url)
                page_now = str(int(page_now) + 1)
            return "\r\n".join(content_dict.values())

    def process_list(self, datas):
        records = datas.get("dto", {}).get("record")
        print(records)
        if records:
            for record in records:
                print(record)
                # 不需要转评的内容
                if record.get("tops") and record.get("rtype") == "R":

                    continue

                item = dict()
                item['code'] = self.code
                item['chinameabbr'] = self.name
                # 时间格式处理  'pub_date': 1578294361000 -->
                pub_date = record.get("actionDate")
                pub_date = self.convert_dt(int(int(pub_date) / 1000))
                item["pub_date"] = pub_date  # 文章发布时间

                title = record.get("subject")[:64]
                if title == "W":
                    title = record.get("body")[:60]

                item['title'] = title  # 文章标题
                codes = record.get("stockAttr")  # 文章谈及股票
                if codes:
                    codes_str = ",".join([j.get("stockName") for j in codes])
                else:
                    codes_str = ''
                item['stockattr'] = codes_str

                article_url = "https://www.taoguba.com.cn/Article/" + str(record.get("rID")) + "/1"
                rid = record.get("rID")
                print(article_url)
                item['link'] = article_url
                detail_resp = self.get(article_url)
                if detail_resp:
                    detail_page = detail_resp.text
                    article = self.parse_detail(detail_page, rid)
                    if article:
                        article = self._process_content(article)
                        item['article'] = article
                        print(item)
                        time.sleep(random.randint(1, 3))

            # # 生成下一次爬取的 url 相当于翻页
            # more_timestamp = records[-1].get("actionDate")
            # more_url = self.refresh_url + urlencode(self.make_query_params(more_timestamp))
            # print("more: >>", more_url)
            # self.refresh(more_url)

    def refresh(self, start_url):
        # 该函数与process_list互相调用
        resp = self.get(start_url)
        print(resp)
        if resp:
            datas = json.loads(resp.text)
            print(datas)
            if not datas.get("status"):
                print(datas.get("errorMessage"))
                return
            else:
                self.process_list(datas)

    def start(self):
        tstamp = int(time.time()) * 1000  # js 中的时间戳 第一次这个值选用当前时间
        query_params = self.make_query_params(tstamp)
        print(query_params)
        start_url = self.refresh_url + urlencode(query_params)
        print(start_url)
        self.refresh(start_url)


if __name__ == "__main__":
    Taoguba("格力电器", "sz000651").start()
