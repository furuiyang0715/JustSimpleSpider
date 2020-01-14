"""
利用 sqlite 记录系统信息
"""
import os
import sqlite3
import sys

sys.path.insert(0, "./..")

from chinabank.configs import DB_FILE


class Recorder(object):
    def __init__(self, restart: False):
        self.db_file = DB_FILE
        self.restart = restart  # 是否销毁数据库重新开始

        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def _create_table(self):
        if self.restart:
            if os.path.isfile(self.db_file):
                os.remove(self.db_file)
                print("数据库文件删除成功 ")
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            self.cursor.execute('create table chinabank(id int  primary key, nums int, per_num int)')
        else:

            print("已经建好 sqlite 数据库")

    def insert(self, dt: int, nums: int, per_num: int):
        """
        向数据库中插入记录
        :param dt:  当前的更新时间
        :param nums:  文章总数 从页面匹配得到
        :param per_num: 每页显示的个数
        :return:
        """
        sql = r'insert into chinabank values ({}, {}, {});'.format(dt, nums, per_num)
        print("插入本次的信息: ", sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def get_all(self):
        ret = self.cursor.execute(r'select * from chinabank;')
        lst = ret.fetchall()
        return lst

    def get_last(self):
        ret = self.cursor.execute(r'select * from chinabank where id = (select max(id) from chinabank);')
        return ret.fetchone()



# d = Recorder(True)

d = Recorder(False)

d._create_table()
# d.insert(*(20200101, 0, 15))

print(d.get_all())
print(d.get_last())







