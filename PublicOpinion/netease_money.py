import datetime
import re

import demjson
import pymysql
import requests
from gne import GeneralNewsExtractor

from PublicOpinion.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_USER, MYSQL_DB, LOCAL, LOCAL_MYSQL_HOST, \
    LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase


class Money163(object):
    def __init__(self):
        self.list_url = "http://money.163.com/special/00251G8F/news_json.js"
        self.extractor = GeneralNewsExtractor()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
                   }
        self.local = LOCAL
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
        self.table = "netease_money"
        self.error_detail = []

    def _parse_list(self, body):
        js_obj = re.findall(r"news:(.*)\};", body)[0]
        py_obj = demjson.decode(js_obj)
        for type in py_obj:  # 得到每一个子主题
            for data in type:
                yield data

    def _parse_detail(self, detail_url):
        try:
            page = requests.get(detail_url, headers=self.headers).text
            result = self.extractor.extract(page)
            content = result.get("content")
        except:
            return
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

    def _save(self, to_insert):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            print("重复")
            return 1
        except:
            print("失败")
        else:
            return count

    def _start(self):
        list_resp = requests.get(self.list_url)
        if list_resp.status_code == 200:
            body = list_resp.text
            ret = self._parse_list(body)
            for one in ret:
                # print(one)
                item = dict()
                link = one.get("l")
                item['link'] = link
                item['title'] = one.get("t")

                # 在返回的 json 数据中 最新的数据在最前面 定时+增量 只需要爬取大于当前时间一天之前的新闻
                # 保险起见 设置为 2
                dt = datetime.datetime.today() - datetime.timedelta(days=2)
                pub_date = one.get("p")
                pt = datetime.datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S")
                if pt < dt:
                    print(pt)
                    print(dt)
                    print('网易财经增量完毕 ')
                    return

                item['pub_date'] = pub_date
                article = self._parse_detail(one.get("l"))
                if article:
                    item['article'] = article
                    print(item)
                    ret = self._save(item)
                    if not ret:
                        print("保存失败 ")
                        self.error_detail.append(link)
                else:
                    self.error_detail.append(link)


if __name__ == "__main__":
    m = Money163()
    m._start()
