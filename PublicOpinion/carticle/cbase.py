import datetime
import json
import random
import re
import string
import sys
import time
import traceback
from urllib.parse import urlencode

import pymysql
import requests
from lxml import html

from PublicOpinion.configs import LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL_PROXY_URL, PROXY_URL
from PublicOpinion.sql_pool import PyMysqlPoolBase


class CArticleBase(object):
    # 东财-财富号的基类
    def __init__(self, key):
        self.local = LOCAL
        self.key = key
        print(self.key, "\n\n\n")
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
        }
        self.table = "eastmoney_carticle"
        self.error_detail = []
        self.error_list = []
        self.proxy = self._get_proxy()
        self.dt_format = '%Y-%m-%d %H:%M:%S'
        self.limit_time = datetime.datetime(2020, 2, 1)
        self.use_proxy = 1

    def _init_pool(self):
        if self.local:
            conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
            }
            self.db = LOCAL_MYSQL_DB
        else:
            conf = {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
                "db": MYSQL_DB,
            }
            self.db = MYSQL_DB
        self.sql_pool = PyMysqlPoolBase(**conf)

    def make_query_params(self, msg, page):
        query_params = {
            'type': '8224',  # 该参数表明按时间排序
            'pageindex': str(page),
            'pagesize': str(self.page_size),
            'keyword': msg,
            'name': 'caifuhaowenzhang',
            'cb': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 21)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def contract_sql(self, to_insert):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}`.`{}` '''.format(
            self.db, self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _save(self, to_insert):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            # print("重复 ")
            return 1
        except:
            print("失败")
            traceback.print_exc()
            return
        else:
            return count

    def _get_proxy(self):
        if self.local:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            return requests.get(PROXY_URL).text.strip()

    def _delete_detail_404(self, url):
        delete_sql = f"delete from `{self.table}` where link = {url};"
        ret = self.sql_pool.delete(delete_sql)
        self.sql_pool.end()
        if ret:
            print(f"删除无效的 url: {url}")

    def _crawl(self, url, proxy):
        proxies = {'http': proxy}
        r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        return r

    def _get(self, url):
        if self.use_proxy:
            count = 0
            while True:
                count = count + 1
                try:
                    resp = self._crawl(url, self.proxy)
                    if resp.status_code == 200:
                        return resp
                    elif resp.status_code == 404:
                        self._delete_detail_404(url)
                        return None
                    elif count > 2:
                        print(f'抓取网页{url}最终失败')
                        break
                    else:
                        self.proxy = self._get_proxy()
                        print(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
                except:
                    self.proxy = self._get_proxy()
                    print(f'代理失败,更换代理{self.proxy} \n')
        else:
            try:
                resp = requests.get(url)
            except:
                return
            return resp

    def _parse_detail(self, detail_page):
        doc = html.fromstring(detail_page)
        article_body = doc.xpath('//div[@class="article-body"]/*')
        contents = []
        for p_node in article_body:
            children = p_node.getchildren()
            children_tags = [child.tag for child in children]
            if children_tags and "img" in children_tags:
                img_links = p_node.xpath("./img/@src")  # list
                contents.append(",".join(img_links))
            else:
                contents.append(p_node.text_content())
        contents = "\r\n".join(contents)
        return contents

    def transferContent(self, content):
        if content is None:
            return None
        else:
            string = ""
            for c in content:
                if c == '"':
                    string += '\\\"'
                elif c == "'":
                    string += "\\\'"
                elif c == "\\":
                    string += "\\\\"
                else:
                    string += c
            return string

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
        return "".join(params)

    def _get_list(self, list_url):
        resp = self._get(list_url)
        if resp:
            return resp.text
        else:
            self.error_list.append(list_url)

    def _get_detail(self, detail_url):
        resp = self._get(detail_url)
        if resp:
            return resp.text
        else:
            self.error_detail.append(detail_url)

    def _parse_list(self, list_page):
        try:
            json_data = re.findall(r'jQuery\d{21}_\d{13}\((\{.*?\})\)', list_page)[0]
            list_data = json.loads(json_data).get("Data")
        except:
            return None
        else:
            if list_data:
                return list_data
            else:
                return []

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass

    def close(self):
        try:
            self.sql_pool.dispose()
        except:
            pass

    def start(self):
        try:
            self._start()
        except:
            traceback.print_exc()
        finally:
            self.close()

    def _start(self):
        # 本类是针对某一个具体的 code 来进行爬取的
        # 所以在  _start 之外还会有一个总的 "调度函数"

        self._init_pool()

        # (1) 生成 list_url
        for page in range(1, 2):
            # print(page)
            list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
            # print(list_url)

            # (2) 获取列表页
            list_page = self._get_list(list_url)
            # print(list_page)

            # (3) 从列表页解析数据 返回列表
            list_infos = self._parse_list(list_page)
            # print(pprint.pformat(list_infos))

            if list_infos:
                # # 增量的过程中不再继续爬取
                # show_times = [datetime.datetime.strptime(info.get("ShowTime"), self.dt_format) for info in list_infos]
                # # print(show_times)
                # if max(show_times) < self.limit_time:
                #     print("增量完毕")
                #     return

                count = 0
                # (4) 解析详情页 保存数据
                for data in list_infos:
                    item = dict()
                    item['code'] = self.key
                    link = data.get("ArticleUrl")
                    item['link'] = link
                    item['title'] = data.get("Title")
                    item['pub_date'] = data.get("ShowTime")
                    detail_page = self._get_detail(link)
                    if detail_page:
                        article = self._parse_detail(detail_page)
                        # 对文章进行处理 以防插入失败..
                        article = self._process_content(article)
                        item['article'] = article
                        print("item", item)
                        ret = self._save(item)
                        if not ret:
                            print(f"插入失败 {item.get('link')}")
                        else:
                            count += 1
                            if count > 10:
                                self.sql_pool.end()
                                count = 0
                self.sql_pool.end()  # self.sql_pool.connection.commit()
                print(f"第{page}页保存成功")
        self.close()


if __name__ == "__main__":
    demo = CArticleBase(key='视源股份')
    demo.local = True
    demo.start()