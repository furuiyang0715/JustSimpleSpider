import json
import logging
import random
import re
import string
import time
from urllib.parse import urlencode

import pymysql
import requests
from lxml import html

from PublicOpinion.configs import MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, DC_HOST, DC_PORT, \
    DC_USER, DC_PASSWD, DC_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase


logger = logging.getLogger()


class CArticle(object):
    def __init__(self, key):
        self.local = True
        self.abu = True
        self.key = key
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",


        }
        self.db = MYSQL_DB
        self.table = "eastmoney_carticle"
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.sql_pool = PyMysqlPoolBase(**conf)
        self.proxy = self._get_proxy()
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
        retry = 2
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
                    retry -= 1
                    if retry <= 0:
                        return None
                    return self._abu_get(url)
            except:
                retry -= 1
                if retry <= 0:
                    return None
                return self._abu_get(url)

    def _get_proxy(self):
        if self.local:
            r = requests.get('http://192.168.0.102:8888/get')
        else:
            r = requests.get('http://172.17.0.5:8888/get')
        proxy = r.text
        return proxy

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
        select_all_sql = f"select link from {self.table} where article is NULL;"
        links = self.sql_pool.select_many(select_all_sql, size=20)
        # links = self.sql_pool.select_all(select_all_sql)
        return links

    def _update_detail(self, link, artilce):
        update_sql = f"update {self.table} set article = '{artilce}' where link = '{link}';"
        try:
            ret = self.sql_pool.update(update_sql)
        except:
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
        c = CArticle(key)
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
        elif start and not end:
            for key in self.keys[start:]:
                self._start_instance(key)
        elif not start and end:
            for key in self.keys[:end]:
                self._start_instance(key)
        else:
            for key in self.keys[start: end]:
                self._start_instance(key)

    def _start_rest_detail(self):
        c = CArticle("")
        while True:
            links = c._select_rest_all_links()
            if len(links) < 20:
                break
            # print(links)
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
        c = CArticle(key)
        links = c._select_key_links()
        print(links)
        count = 0
        for link in links:
            link = link.get("link")
            detail_resp = c._get(link)
            print(detail_resp)
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
            # self._start_rest_detail()


if __name__ == "__main__":
    s = Schedule()
    # s.run_list(key="格力电器")

    import os
    key = os.environ.get("KEY", "格力电器")
    s.run_detail(key=key)
