import datetime
import pprint
import re
import sys
import traceback

import pymysql
import requests
from gne import GeneralNewsExtractor
from lxml import html

from PublicOpinion.configs import LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_DB, MYSQL_USER
from PublicOpinion.sql_pool import PyMysqlPoolBase


class STCN_Base(object):
    def __init__(self):
        self.table = "stcn_info"
        self.local = True
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

    def _get(self, url):
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.text

    def _parse_detail(self, body):
        try:
            doc = html.fromstring(body)
            node = doc.xpath("//div[@class='txt_con']")[0]
            content = node.text_content()
        except:
            return None
        else:
            return content

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

    def _contract_sql(self, to_insert):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        ks = sorted(ks)  # article,link,pub_date,title
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(self.table) + fields_str + ''' values ''' + values_str + ''';'''
        # return base_sql, tuple(vs)
        return base_sql

    def _save(self, item):
        insert_sql = self._contract_sql(item)
        # print(insert_sql)
        value = (item.get("article"),
                 item.get("link"),
                 item.get("pub_date"),
                 item.get("title"))
        # print(value)
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
        values = [(item.get("article"),
                   item.get("link"),
                   item.get("pub_date"),
                   item.get("title")) for item in items]
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

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass


# ==================================================================================================


class STCN_YaoWen(STCN_Base):
    def __init__(self):
        super(STCN_YaoWen, self).__init__()
        self.list_url = "http://news.stcn.com/"

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = []
        # 题头文章
        first = doc.xpath("//dl[@class='hotNews']")[0]
        title = first.xpath("//dt/a/@title")[0]
        link = first.xpath("//dt/a/@href")[0]
        pub_date = first.xpath("//dd[@class='sj']")[0].text_content()
        pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
        first = dict()
        first['title'] = title
        first['link'] = link
        first['pub_date'] = pub_date
        detail_body = self._get(link)
        if detail_body:
            article = self._parse_detail(detail_body)
            if article:
                first['article'] = article
                items.append(first)

        # 列表文章
        columns = doc.xpath("//ul[@class='news_list']/li")
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath("./p[@class='tit']/a/@title")[0]
            link = column.xpath("./p[@class='tit']/a/@href")[0]
            pub_date = column.xpath("./p[@class='sj']")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            # print(title, link, pub_date)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    # print(item)
                    items.append(item)
        print("num is ", num)
        return items

    def _start(self):
        list_body = self._get(self.list_url)
        if list_body:
            items = self._parse_list_body(list_body)
            ret = self._save_many(items)
            if ret:
                print("批量保存数据成功 ")
            else:
                count = 0
                for item in items:
                    print(item)
                    ret = self._save(item)
                    if not ret:
                        print("保存单个失败 ")
                    count += 1
                    if count > 9:
                        self.sql_pool.end()
                self.sql_pool.dispose()


class STCN_KCB(STCN_YaoWen):
    def __init__(self):
        super(STCN_KCB, self).__init__()
        self.list_url = "http://kcb.stcn.com/news/index.shtml"

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = []
        columns = doc.xpath("//ul[@class='news_list']/li")
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        return items


class STCN_Company(STCN_YaoWen):
    def __init__(self):
        super(STCN_Company, self).__init__()
        self.list_url = "http://company.stcn.com/"


class STCN_Column(STCN_YaoWen):
    def __init__(self):
        super(STCN_Column, self).__init__()
        self.list_url = "http://space.stcn.com"
        self.extractor = GeneralNewsExtractor()

    def _get(self, url):
        resp = requests.get(url)
        # print(resp.encoding)
        if resp.status_code == 200:
            body = resp.text.encode("ISO-8859-1").decode("utf-8")
            return body

    def _parse_detail(self, body):
        try:
            result = self.extractor.extract(body)
            content = result.get("content")
        except:
            return None
        else:
            return content

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath('//div[@id="news_list2"]/dl')
        # print(columns)
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath('./dd[@class="mtit"]/a/@title')[0]
            link = column.xpath('./dd[@class="mtit"]/a/@href')[0]

            pub_date = column.xpath('./dd[@class="mexp"]/span')[0].text_content()
            yesterday = datetime.datetime.today()-datetime.timedelta(days=1)
            before_yesterday = datetime.datetime.today()-datetime.timedelta(days=2)
            pub_date = pub_date.replace("昨天", yesterday.strftime("%Y-%m-%d"))
            pub_date = pub_date.replace("前天", before_yesterday.strftime("%Y-%m-%d"))
            # print(title, link, pub_date)

            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = requests.get(link).text
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        # print(num)
        return items


class STCN_Market(STCN_YaoWen):
    def __init__(self):
        super(STCN_Market, self).__init__()
        self.list_url = "http://stock.stcn.com/"

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath("//ul[@class='news_list']/li")
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath("./p/a/@title")[0]
            link = column.xpath("./p/a/@href")[0]
            pub_date = column.xpath("./p[@class='sj']")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        # print(num)
        return items


# ==================================================================================================

class STCN_Kuaixun(STCN_Base):

    def __init__(self):
        super(STCN_Kuaixun, self).__init__()
        self.format_url = "http://kuaixun.stcn.com/index_{}.shtml"

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath("//ul[@id='news_list2']/li")
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content()
            # print(pub_date)
            pub_time = column.xpath("./i")[0].text_content()
            # print(pub_time)
            pub_date = '{} {}'.format(pub_date, pub_time)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        # print(num)
        return items

    def _start(self):
        for page in range(1, 21):
            print("\nThe page is {}".format(page))
            list_url = self.format_url.format(page)
            list_body = self._get(list_url)
            if list_body:
                items = self._parse_list_body(list_body)
                ret = self._save_many(items)
                if ret:
                    print("批量保存数据成功 ")

                else:
                    for item in items:
                        # print(item)
                        ret = self._save(item)
                        if not ret:
                            print("保存单个失败 ")
                    self.sql_pool.end()


class STCN_Roll(STCN_Kuaixun):
    def __init__(self):
        super(STCN_Roll, self).__init__()
        self.format_url = "http://news.stcn.com/roll/index_{}.shtml"

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath("//ul[@id='news_list2']/li")
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath("./a")[-1].xpath("./@title")[0]
            # print(title)
            link = column.xpath("./a")[-1].xpath("./@href")[0]
            # print(link)
            pub_date = column.xpath("./span")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            # print(pub_date)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                item['article'] = self._process_content(article)
                print(item)
                items.append(item)
        # print(num)
        return items


class STCN_XWPL(STCN_Kuaixun):
    def __init__(self):
        super(STCN_XWPL, self).__init__()
        self.format_url = "http://news.stcn.com/xwpl/{}.shtml"

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath("//ul[@class='news_list']/li")
        # num = 0
        for column in columns:
            # num += 1
            # print(column.tag)
            title = column.xpath("./p[@class='tit']/a/@title")[0]
            # print(title)
            link = column.xpath("./p[@class='tit']/a/@href")[0]
            # print(link)
            pub_date = column.xpath("./p[@class='sj']")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            # print(pub_date)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        # print(num)
        return items


class STCN_DaPan(STCN_Kuaixun):
    def __init__(self):
        super(STCN_DaPan, self).__init__()
        self.format_url = "http://stock.stcn.com/dapan/{}.shtml"

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath("//ul[@id='news_list2']/li")
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        # print(num)
        return items


class STCN_XinGu(STCN_DaPan):
    def __init__(self):
        super(STCN_XinGu, self).__init__()
        self.format_url = "http://stock.stcn.com/xingu/{}.shtml"


class STCN_ZhuLi(STCN_DaPan):
    def __init__(self):
        super(STCN_ZhuLi, self).__init__()
        self.format_url = "http://stock.stcn.com/zhuli/{}.shtml"


class STCN_YanBao(STCN_DaPan):
    def __init__(self):
        super(STCN_YanBao, self).__init__()
        self.format_url = "http://kuaixun.stcn.com/list/kxyb_{}.shtml"


class STCN_BanKuai(STCN_DaPan):
    def __init__(self):
        super(STCN_BanKuai, self).__init__()
        self.format_url = "http://stock.stcn.com/bankuai/{}.shtml"


# ==================================================================================================


if __name__ == "__main__":
    # d = STCN_YaoWen()    # 要闻

    # d = STCN_Kuaixun()    # 快讯

    # d = STCN_Roll()    # 滚动

    # d = STCN_XWPL()    # 评论

    # d = STCN_Column()   # 专栏

    # d = STCN_Market()   # 股市

    # d = STCN_DaPan()   # 大盘

    # d = STCN_BanKuai()   # 版块

    # d = STCN_XinGu()   # 新股

    # d = STCN_ZhuLi()   # 主力

    # d = STCN_YanBao()   # 研报

    d = STCN_Company()   # 公司

    d = STCN_KCB()  # 科创板

    d._start()


