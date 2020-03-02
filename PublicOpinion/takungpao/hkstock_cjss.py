import datetime
import random
import re
import time
import traceback

import pymysql
import requests
from gne import GeneralNewsExtractor
from lxml import html

from PublicOpinion.configs import LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL_PROXY_URL, PROXY_URL
from PublicOpinion.sql_pool import PyMysqlPoolBase


class Base(object):
    def __init__(self):
        self.local = LOCAL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }
        self.use_proxy = 0

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
        if not self.use_proxy:
            return requests.get(url, headers=self.headers)

        count = 0
        while True:
            count += 1
            if count > 10:
                return None
            try:
                proxy = {"proxy": self._get_proxy()}
                print("proxy is >> {}".format(proxy))
                resp = requests.get(url, headers=self.headers, proxies=proxy)
            except:
                traceback.print_exc()
                time.sleep(0.5)
            else:
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 404:
                    return None
                else:
                    print("status_code: >> {}".format(resp.status_code))
                    time.sleep(1)
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
        if not items:
            print("批量数据为空 ")
            return
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


class HKStock_CJSS(Base):

    def __init__(self):
        super(HKStock_CJSS, self).__init__()
        self.page = 11
        self.name = '财经时事'
        self.first_url = 'http://finance.takungpao.com/hkstock/cjss/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/cjss/index_{}.html"
        self.extractor = GeneralNewsExtractor()
        self.table = 'takungpao'
        self.fields = ['link', 'title', 'pub_date', 'article']

    def _parse_detail(self, body):
        result = self.extractor.extract(body)
        content = result.get("content")
        return content

    def parse_list(self, body):
        items = []
        doc = html.fromstring(body)
        news_list = doc.xpath("//div[@class='m_txt_news']/ul/li")
        # print(news_list)
        # print(len(news_list))
        for news in news_list:
            item = {}
            title = news.xpath("./a[@class='a_title']")
            if not title:
                title = news.xpath("./a[@class='a_title txt_blod']")
            title = title[0].text_content()
            # print(title)
            item['title'] = title
            pub_date = news.xpath("./a[@class='a_time txt_blod']")
            if not pub_date:
                pub_date = news.xpath("./a[@class='a_time']")

            link = pub_date[0].xpath("./@href")[0]
            # print(link)
            item['link'] = link

            pub_date = pub_date[0].text_content()
            # print(pub_date)
            item['pub_date'] = pub_date
            items.append(item)

            detail_resp = self.get(link)
            if detail_resp:
                article = self._parse_detail(detail_resp.text)
                if article:
                    article = self._process_content(article)
                    item['article'] = article
        return items

    def _start(self):
        for page in range(1, self.page+1):
            print(">>> ", page)
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)

            list_resp = self.get(list_url)
            if list_resp:
                items = self.parse_list(list_resp.text)
                print(items)
                print()
                self.save(items)


if __name__ == "__main__":
    cjss = HKStock_CJSS()
    cjss.start()