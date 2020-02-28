import datetime
import re
import traceback

import pymysql

from PublicOpinion.configs import LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase


class ClsBase(object):
    # 财联社-基类
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
            self._start()
        except:
            traceback.print_exc()
