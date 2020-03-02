# -*- coding: utf-8 -*-
import datetime
import json
import pprint
import random
import re
import time
import traceback
from urllib.parse import urlencode

import pymysql
import requests
from bs4 import BeautifulSoup
from lxml import html

from PublicOpinion.configs import LOCAL_PROXY_URL, PROXY_URL, LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, \
    LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase
from PublicOpinion.taoguba.tgb_base import ScheduleBase


class Base(object):
    def __init__(self):
        self.local = LOCAL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }

    def _init_pool(self):
        if self.local:
            conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
            }
        else:
            conf = {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
                "db": MYSQL_DB,
            }
        self.sql_pool = PyMysqlPoolBase(**conf)

    def _get_proxy(self):
        if self.local:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            random_num = random.randint(0, 10)
            if random_num % 2:
                time.sleep(1)
                return requests.get(PROXY_URL).text.strip()
            else:
                return requests.get(LOCAL_PROXY_URL).text.strip()

    def get(self, url):
        count = 0
        while True:
            count += 1
            if count > 10:
                return None
            try:
                resp = requests.get(url, headers=self.headers, proxies={"proxy": self._get_proxy()})
            except:
                traceback.print_exc()
                time.sleep(0.5)
            else:
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 404:
                    return None
                else:
                    pass

    def convert_dt(self, time_stamp):
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d

    def _contract_sql(self, to_insert):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        ks = sorted(ks)
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql

    def _filter_char(self, test_str):
        # 处理特殊的空白字符
        # '\u200b' 是 \xe2\x80\x8b
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            test_str = test_str.replace(cha, '')
        test_str = test_str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        return test_str

    def _process_content(self, vs):
        # 去除 4 字节的 utf-8 字符，否则插入mysql时会出错
        try:
            # python UCS-4 build的处理方式
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # python UCS-2 build的处理方式
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        params = list()
        for v in vs:
            # 对插入数据进行一些处理
            nv = highpoints.sub(u'', v)
            nv = self._filter_char(nv)
            params.append(nv)
        content = "".join(params).strip()
        return content

    def _get_values(self, item: dict):
        # self.fields: []  插入所需字段列表 同时与上文的 ks = sorted(ks) 对应
        value = tuple(item.get(field) for field in sorted(self.fields))
        return value

    def _save(self, item):
        insert_sql = self._contract_sql(item)
        value = self._get_values(item)
        try:
            ret = self.sql_pool.insert(insert_sql, value)
        except pymysql.err.IntegrityError:
            print("重复数据 ")
            return 1
        except:
            traceback.print_exc()
        else:
            return ret

    def _save_many(self, items):
        values = [self._get_values(item) for item in items]   # list of tuple
        insert_many_sql = self._contract_sql(items[0])
        try:
            ret = self.sql_pool.insert_many(insert_many_sql, values)
        except pymysql.err.IntegrityError:
            print("批量中有重复数据")
        except:
            traceback.print_exc()
        else:
            return ret
        finally:
            self.sql_pool.end()

    def save_one(self, item):
        self._save(item)
        self.sql_pool.end()

    def save(self, items):
        ret = self._save_many(items)
        if not ret:
            print("批量保存失败 开始单独保存 .. ")
            count = 0
            for item in items:
                print(item)
                self._save(item)
                count += 1
                if count > 9:
                    self.sql_pool.end()
                    count = 0
            # self.sql_pool.dispose()
            self.sql_pool.end()
        else:
            print("批量成功..")
            print(items)
            print(len(items))

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass

    def start(self):
        try:
            self._init_pool()
            self._start()
        except:
            traceback.print_exc()


class Taoguba(Base):
    def __init__(self, name, code):
        super(Taoguba, self).__init__()

        self.refresh_url = 'https://www.taoguba.com.cn/quotes/getStockUpToDate?'
        self.page_num = 100
        self.name = name
        self.code = code
        self.table = 'taoguba'
        self.fields = [
            'pub_date',
            'code',
            'chinameabbr',    # 股票中文简称
            'stockattr',      # 相关个股
            'title',
            'link',
            'article',
        ]

    def make_query_params(self, timestamp):
        """
        拼接请求参数
        :param code:
        :param timestamp:
        :return:
        """
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

    def _start(self):
        tstamp = int(time.time()) * 1000  # js 中的时间戳 第一次这个值选用当前时间
        query_params = self.make_query_params(tstamp)
        print(query_params)
        start_url = self.refresh_url + urlencode(query_params)
        print(start_url)
        self.refresh(start_url)

    def refresh(self, start_url):
        resp = self.get(start_url)
        print(resp)
        if resp:
            datas = json.loads(resp.text)
            print(datas)
            if not datas.get("status"):
                print(datas.get("errorMessage"))
                return
            records = datas.get("dto", {}).get("record")
            # print(records)
            if records:
                for record in records:
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

                    title = record.get("subject")
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
                        # TODO 文本处理
                        article = self._process_content(article)
                        item['article'] = article
                        print(item)
                        time.sleep(10)
                        self.save_one(item)


class TgbSchedule(ScheduleBase):
    def start(self):
        for code, name in self.lower_keys.items():
            print(code, name)
            if not name:
                print(">> ", code)
                continue
            instance = Taoguba(name=name, code=code)
            instance.start()


if __name__ == "__main__":
    sche = TgbSchedule()
    sche.start()

    # tt = Taoguba('sz300150', '世纪瑞尔')
    # tt.start()
    # url = 'https://www.taoguba.com.cn/Article/5709754/1'
    # detail_page = tt.get(url).text
    # print(detail_page)
    # ret = tt._parse_page(detail_page)
    # print(ret)
