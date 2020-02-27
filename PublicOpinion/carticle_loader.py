# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import re
import string
import time
import traceback
from urllib.parse import urlencode

import pymysql
import requests
from lxml import html
import sys

sys.path.append("./../")
from PublicOpinion.configs import MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, DC_HOST, DC_PORT, \
    DC_USER, DC_PASSWD, DC_DB, LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, LOCAL_PROXY_URL, PROXY_URL
from PublicOpinion.sql_pool import PyMysqlPoolBase


logger = logging.getLogger()
# PROXY_URL = os.environ.get("PROXY_URL", "http://172.17.0.4:8888/{}")   # 远程的代理地址
# LOCAL_PROXY_URL = os.environ.get("LOCAL_PROXY_URL", "http://127.0.0.1:8888/{}")   # 本地的代理url


class CArticleLoder(object):
    def __init__(self, key):
        # 本地运行亦或者是在服务器上运行
        self.local = LOCAL
        # 是否使用阿布云代理
        self.abu = False
        # 股票代码中文简称
        self.key = key
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",


        }
        self.db = MYSQL_DB
        self.table = "eastmoney_carticle"
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
        # 不使用阿布云的情况下 初始化代理
        if not self.abu:
            self.proxy = self._get_proxy()
        # 记录出错的列表页 以及 详情页 url
        self.error_detail = []
        self.error_list = []

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
            logger.warning("重复 ")
        except:
            logger.warning("失败")
        else:
            return count

    def _abu_get(self, url):
        """使用阿布云代理 默认失败后重新发起请求"""
        proxy_host = "http-cla.abuyun.com"
        proxy_port = 9030
        # 代理隧道验证信息
        proxy_user = "H74JU520TZ0I2SFC"
        proxy_pass = "7F5B56602A1E53B2"
        proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxy_host,
            "port": proxy_port,
            "user": proxy_user,
            "pass": proxy_pass,
        }
        proxies = {
            "http": proxy_meta,
            "https": proxy_meta,
        }
        retry = 2  # 重试三次 事不过三^_^
        while True:
            try:
                resp = requests.get(url,
                                    proxies=proxies,
                                    headers=self.headers,
                                    timeout=3,
                                    )
                if resp.status_code == 200:
                    return resp
                else:
                    print(resp.status_code, "retry")
                    retry -= 1
                    if retry <= 0:
                        return None
                    time.sleep(3)
            except:
                print("error retry")
                retry -= 1
                if retry <= 0:
                    return None
                time.sleep(3)

    # def _get_proxy(self):
    #     if self.local:
    #         r = requests.get('http://192.168.0.102:8888/get')
    #     else:
    #         r = requests.get('http://172.17.0.4:8888/get')
    #     proxy = r.text
    #     return proxy

    def _get_proxy(self):
        if self.local:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            return requests.get(PROXY_URL).text.strip()

    # def _get_proxy(self):
    #     # 获取一个可用代理 如果当前没有可用的话 就 sleep 3 秒钟
    #     if self.local:
    #         while True:
    #             count = requests.get(LOCAL_PROXY_URL.format("count"))
    #             if count:
    #                 resp = requests.get(LOCAL_PROXY_URL.format("get"))
    #                 break
    #             else:
    #                 print("当前无可用代理, 等一会儿 ")
    #                 time.sleep(3)
    #         return resp.text
    #     else:
    #         while True:
    #             count = requests.get(PROXY_URL.format("count"))
    #             if count:
    #                 resp = requests.get(PROXY_URL.format("get"))
    #                 break
    #             else:
    #                 print("当前无可用代理, 等一会儿 ")
    #                 time.sleep(3)
    #         return resp.text

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
        if self.abu:
            return self._abu_get(url)

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
                    logger.warning(f'抓取网页{url}最终失败')
                    break
                else:
                    self.proxy = self._get_proxy()
                    logger.warning(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
            except:
                self.proxy = self._get_proxy()
                logger.warning(f'代理失败,更换代理{self.proxy} \n')

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

    def _select_key_links(self):
        select_all_sql = f"select link from {self.table} where code = '{self.key}' and article is NULL;"
        # links = self.sql_pool.select_many(select_all_sql, size=10)
        links = self.sql_pool.select_all(select_all_sql)
        return links

    def _select_rest_all_links(self):
        select_all_sql = f"select id, link from {self.table} where article is NULL;"
        # links = self.sql_pool.select_many(select_all_sql, size=20)
        links = self.sql_pool.select_all(select_all_sql)
        return links

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

    def _update_detail(self, link, article):
        # 直接插入文本内容可能出错 需对其进行处理
        # article = self.transferContent(article)
        article = self._process_content(article)
        print("文章内容是: \n", article)
        update_sql = f"update {self.table} set article =%s where link =%s;"
        try:
            ret = self.sql_pool.update(update_sql, [(article), (link)])
            # ret = self.sql_pool.update(update_sql)
        except:
            traceback.print_exc()
            print("插入失败")
            return None
        else:
            return ret

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

    def _save_one_page_list(self, page):
        list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
        list_page = self._get_list(list_url)
        if list_page:
            list_infos = self._parse_list(list_page)  # list
            if not list_infos:
                logger.info(f"{self.key} 爬取完毕 ")
                return

            for data in list_infos:
                item = dict()
                item['code'] = self.key
                link = data.get("ArticleUrl")
                item['link'] = link
                item['title'] = data.get("Title")
                item['pub_date'] = data.get("ShowTime")
                print("item", item)
                ret = self._save(item)
                if not ret:
                    logger.warning(f"插入失败 {item}")
            self.sql_pool.end()  # self.sql_pool.connection.commit()
            print(f"第{page}页保存成功")
            return page

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass


class Schedule(object):
    def __init__(self):
        self.keys = sorted(self.dc_info().values())

    def dc_info(self):  # {'300150.XSHE': '世纪瑞尔',
        """
        从 datacanter.const_secumain 数据库中获取当天需要爬取的股票信息
        返回的是 股票代码: 中文名简称 的字典的形式
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
            in (select distinct SecuCode from const_secumain);""")
        dc_info = {r[0]: r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return dc_info

    def _start_instance(self, key):
        c = CArticleLoder(key)
        now = lambda: time.time()
        t1 = now()
        cur = t1
        for page in range(1, 50000):
            page = c._save_one_page_list(page)
            if not page:
                break
            print(f"第 {page} 页, 累计用时 {now() - t1}, 当前页用用时 {now() - cur} ")
            cur = now()
        c.sql_pool.dispose()
        with open("record.txt", "a+") as f:
            f.write(f"{key}: error_list: {c.error_list}, error_detail: {c.error_detail}\r\n")

    def run_list(self, start=None, end=None, key=None):
        if key:
            self._start_instance(key)
        else:
            for key in self.keys[start: end]:
                self._start_instance(key)

    def _start_rest_detail(self):
        c = CArticleLoder("")
        while True:
            links = c._select_rest_all_links()
            if len(links) < 20:
                break
            print(links)
            print("length:", len(links))
            for link in links:
                link = link.get("link")
                detail_resp = c._get(link)
                print("resp:", detail_resp)
                if detail_resp:
                    detail_page = detail_resp.text
                    article = c._parse_detail(detail_page)
                    # print("article: ", article)
                    ret = c._update_detail(link, article)
                    if ret:
                        print("更新成功")
                    else:
                        print("更新失败")
            print("一次提交")
            c.sql_pool.end()

    def _start_ins_detail(self, key):
        c = CArticleLoder(key)
        links = c._select_key_links()
        print(links)
        count = 0
        for link in links:
            link = link.get("link")
            print("当前处理连接:", link)
            detail_resp = c._get(link)
            print("响应结果: ", detail_resp)
            if detail_resp:
                detail_page = detail_resp.text
                article = c._parse_detail(detail_page)
                ret = c._update_detail(link, article)
                if ret:
                    print("更新成功")
                else:
                    print("更新失败")
                count += 1
                if count > 9:
                    print("提交")
                    c.sql_pool.end()
                    count = 0
        c.sql_pool.dispose()

    def run_detail(self, start=None, end=None, key=None):
        if key:
            self._start_ins_detail(key)
        else:
            for k in self.keys[start: end]:
                print(k)
                self._start_ins_detail(k)

    def last_update_200(self):
        c = CArticleLoder("")
        links = c._select_rest_all_links()
        # print(links)
        # [{'id': 1717, 'link': 'http://caifuhao.eastmoney.com/news/20200203193311525228570'},
        final_fail_ids = []
        count = 0
        for info in links:
            print(info)
            detail_page = c._get_detail(info['link'])
            if detail_page:
                article = c._parse_detail(detail_page)
                ret = c._update_detail(info['link'], article)
                print(ret)
                if ret:
                    print("更新成功 ")
                    count += 1
                else:
                    print("更新失败")
                if count > 9:
                    c.sql_pool.end()
                    count = 0
                    print("提交 ")
            else:
                final_fail_ids.append(info['link'])

        print(final_fail_ids)


if __name__ == "__main__":
    s = Schedule()
    s.last_update_200()
    # print(len(s.keys))   # 3923
    # print(s.keys.index('华邦健康'))
    # print(s.keys[500])
    # s.run_list(key="格力电器")
    # import os
    # key = os.environ.get("KEY", "格力电器")
    # start = os.environ.get("START", 0)
    # end = os.environ.get("END", 0)
    # print(key, start, end)
    # s.run_detail(key=key, start=int(start), end=int(end))
    pass
