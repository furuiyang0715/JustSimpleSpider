import re

import demjson
import pymysql
import requests
from gne import GeneralNewsExtractor

from PublicOpinion.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_USER, MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase


class Money163(object):
    def __init__(self):
        self.list_url = "http://money.163.com/special/00251G8F/news_json.js"
        self.extractor = GeneralNewsExtractor()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
                   }
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.sql_pool = PyMysqlPoolBase(**conf)
        self.db = MYSQL_DB
        self.table = "netease_money"

    def _parse_list(self, body):
        js_obj = re.findall(r"news:(.*)\};", body)[0]
        py_obj = demjson.decode(js_obj)
        for type in py_obj:  # 得到每一个子主题
            for data in type:
                yield data

    def _parse_detail(self, detail_url):
        page = requests.get(detail_url, headers=self.headers).text
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
                item['link'] = one.get("l")
                item['title'] = one.get("t")
                item['pub_date'] = one.get("p")
                item['article'] = self._parse_detail(one.get("l"))
                print(item)
                ret = self._save(item)
                if not ret:
                    print("保存失败 ")


if __name__ == "__main__":
    m = Money163()
    m._start()
