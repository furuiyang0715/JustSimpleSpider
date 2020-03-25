# -*- coding: utf-8 -*-
import base64
import logging
import re
import time
import traceback

import pymysql
import requests
from gne import GeneralNewsExtractor
from lxml import html

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from GovSpiders.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL, LOCAL_MYSQL_HOST, \
    LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB
from GovSpiders.sql_client import PyMysqlBase

logger = logging.getLogger()


class BaseSpider(object):
    def __init__(self):
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        # 是否在本地运行
        self.local = LOCAL
        # shodua
        self.use_js = True

        # selenium 的 Chrome 的相关配置
        if not self.use_js:
            if self.local:
                self.browser = webdriver.Chrome()
            else:
                self._check_selenium_status()
                self.browser = webdriver.Remote(
                    command_executor="http://chrome:4444/wd/hub",
                    desired_capabilities=DesiredCapabilities.CHROME
                )
            self.browser.implicitly_wait(5)
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
        self.sql_client = PyMysqlBase(**conf)
        self.extractor = GeneralNewsExtractor()

        self.error_list = []
        self.error_detail = []
        self.nums = 0

    def _check_selenium_status(self):
        """
        检查 selenium 服务端的状态
        """
        while True:
            i = 0
            try:
                resp = requests.get("http://chrome:4444/wd/hub/status", timeout=0.5)
            except:
                i += 1
                if i > 10:
                    raise
            else:
                logger.info(resp.text)
                break

    def __del__(self):
        try:
            self.browser.close()
        except:
            pass

    def fetch_page(self, url):
        if self.use_js:
            return self.js_get_page(url)

        retry = 2
        try:
            self.browser.get(url)
            page = self.browser.page_source
        except:
            retry -= 1
            if retry < 0:
                return
            print('Crawling Failed', url)
            print('try to fetch again')
            time.sleep(3)
            return self.fetch_page(url)
        else:
            return page

    def _get_refer_url(self, body):
        """获取重定向之后的网址"""
        doc = html.fromstring(body)
        script_content = doc.xpath("//script")[0].text_content()
        re_str = r"var(.+?).split"
        ret = re.findall(re_str, script_content)[0]
        # print("正则结果: ", ret)
        ret = ret.lstrip("|(")
        ret = ret.rstrip("')")
        ret_lst = ret.split("|")
        names = ret_lst[0::2]
        params = ret_lst[1::2]
        info = dict(zip(names, params))
        factor = sum([ord(ch) for ch in info.get("wzwsquestion")]) * int(info.get("wzwsfactor")) + 0x1b207
        raw = f'WZWS_CONFIRM_PREFIX_LABEL{factor}'
        refer_url = info.get("dynamicurl") + '?wzwschallenge=' + base64.b64encode(raw.encode()).decode()
        return "http://www.pbc.gov.cn" + refer_url

    def js_get_page(self, url):
        s = requests.Session()
        h1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.pbc.gov.cn',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        }
        resp1 = s.get(url, headers=h1)
        cookie1 = resp1.headers.get("Set-Cookie").split(";")[0]
        origin_text = resp1.text
        redirect_url = self._get_refer_url(origin_text)
        h1.update({
            'Cookie': cookie1,
            'Referer': 'http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index1.html',
        })
        resp2 = s.get(redirect_url, headers=h1)
        text = resp2.text.encode("ISO-8859-1").decode("utf-8")
        return text

    def gne_parse_detail(self, page):
        result = self.extractor.extract(page)
        content = result.get("content")
        return content

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

    def _process_item(self, item):
        return item

        # item.update({"article": self._process_content(item.get("article"))})
        # return item

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

    def save(self, item):
        to_insert = self._process_item(item)
        insert_sql, values = self.contract_sql(to_insert)

        try:
            ret = self.sql_client.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            # logger.warning("重复", to_insert)
            return 1
        except:
            traceback.print_exc()
        else:
            print("本次新增记录{}".format(item))
            self.nums += 1
            return ret

    def _get_page_url(self, page_num):
        if self.start_url:
            return self.start_url.format(page_num)
        elif page_num == 1:
            return self.first_url
        else:
            return self.format_url.format(page_num)

    def process_list(self, page_num):
        page_url = self._get_page_url(page_num)
        list_retry = 2
        while True:
            try:
                list_page = self.fetch_page(page_url)
                if list_page:
                    items = self._parse_list_page(list_page)
                else:
                    raise
            except:
                print("list page {} retry ".format(page_num))
                list_retry -= 1
                if list_retry < 0:
                    return
                # self.process_list(page_num)
            else:
                return items

    def process_detail(self, link):
        detail_retry = 2
        while True:
            try:
                detail_page = self.fetch_page(link)
                if detail_page:
                    article = self._parse_detail_page(detail_page)
                else:
                    raise
            except:
                print("detail page {} retry ".format(link))
                detail_retry -= 1
                if detail_retry < 0:
                    return
            else:
                return article

    def _start(self, page_num):
        print("page num is {}\n".format(page_num))
        items = self.process_list(page_num)
        if items:
            for item in items:
                link = item["link"]
                article = self.process_detail(link)
                if article:
                    item['article'] = article
                    ret = self.save(item)
                    if not ret:
                        self.error_detail.append(item.get("link"))
                else:
                    self.error_detail.append(link)
        else:
            self.error_list.append(self._get_page_url(page_num))

    def start(self, page_num):
        try:
            self._create_table()
            self._start(page_num)
        except:
            traceback.print_exc()


if __name__ == "__main__":
    runner = BaseSpider()

    detail_url = "http://www.pbc.gov.cn/diaochatongjisi/116219/116225/3936095/index.html"
    detail_page = runner.fetch_page(detail_url)
    # print(runner.js_get_page(detail_url))

    # detail_url_with_table = "http://www.pbc.gov.cn/diaochatongjisi/116219/116225/3936088/index.html"
    # detail_page = runner.fetch_page(detail_url_with_table)
    # article = runner.parse_detail(detail_page)
    # print(article)
