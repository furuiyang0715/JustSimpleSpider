import datetime
import json
import pprint
import random
import re
import sys
import time
import traceback

import pymysql
import requests

from PublicOpinion.configs import LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase

now = lambda: int(time.time())


class Telegraphs(object):
    def __init__(self):
        self.local = LOCAL
        self.this_last_dt = None
        self.items = []
        self.name = '财新社-电报'
        self.url_format = 'https://www.cls.cn/nodeapi/telegraphs?refresh_type=1&rn=20&last_time={}&sign=56918b10789cb8a977c518409e7f0ced'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }
        self.table = 'cls_telegraphs'

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

    def refresh(self, url):
        # 只显示一天的数据
        resp = requests.get(url, headers=self.headers)
        # print(resp)

        if resp.status_code == 200:
            py_data = json.loads(resp.text)
            infos = py_data.get("data").get('roll_data')
            # print(infos)
            if not infos:
                return

            for info in infos:
                item = {}
                title = info.get("title")
                if not title:
                    title = info.get("content")[:20]
                item['title'] = title
                pub_date = info.get("ctime")
                content = info.get("content")
                item['pub_date'] = self.convert_dt(pub_date)
                item['article'] = content
                self.items.append(item)

            dt = infos[-1].get('ctime')
            if dt == self.this_last_dt:
                print("增量完毕 .. ")
                return
            self.this_last_dt = dt
            # dt - 1 是为了防止临界点重复值 尽量 insert_many 成功。
            next_url = self.url_format.format(dt-1)
            time.sleep(random.randint(1, 3))
            print("next_url: ", next_url)
            self.refresh(next_url)

    def _start(self):
        self._init_pool()
        first_url = self.url_format.format(now())
        self.refresh(first_url)
        ret = self._save_many(self.items)
        if not ret:
            print("批量保存失败 开始单独保存 .. ")
            count = 0
            for item in self.items:
                print(item)
                self._save(item)
                count += 1
                if count > 9:
                    self.sql_pool.end()
                    count = 0
            self.sql_pool.dispose()
        else:
            print("批量成功..")
            print(self.items)
            print(len(self.items))

    def convert_dt(self, time_stamp):
        # time_stamp = 1582676474
        d = datetime.datetime.fromtimestamp(time_stamp)
        return d

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `cls_telegraphs`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `title` (`title`,`pub_date`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB AUTO_INCREMENT=34657 DEFAULT CHARSET=utf8mb4 COMMENT='财联社-电报' ; 
        '''
        ret = self.sql_pool._exec_sql(create_sql)
        self.sql_pool.end()
        return ret

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

    def _save(self, item):
        insert_sql = self._contract_sql(item)
        value = (item.get("article"),
                 item.get("pub_date"),
                 item.get("title"))
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


if __name__ == "__main__":
    # dt_test()
    # sys.exit(0)

    tele = Telegraphs()

    # tele._init_pool()
    # ret = tele._create_table()
    # print(ret)
    # sys.exit(0)

    tele._start()
