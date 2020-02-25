import re
import traceback

import pymysql
import requests
from lxml import html

from PublicOpinion.configs import LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
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

    def _add_article(self, item: dict):
        link = item.get("link")
        if link:
            detail_page = self._get(link)
            if detail_page:
                article = self._parse_detail(detail_page)
                if article:
                    item['article'] = article
                    return True
        return False

    def _start(self):
        list_body = self._get(self.list_url)
        if list_body:
            items = self._parse_list_body(list_body)
            count = 0
            for item in items:
                ret = self._save(item)
                if ret:
                    count += 1
                    print("保存成功: {}".format(item))
                else:
                    print("保存失败: {}".format(item))
                if count > 9:
                    self.sql_pool.end()
                    print("提交 .. ")
                    count = 0
            self.sql_pool.dispose()

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass