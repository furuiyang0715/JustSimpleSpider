import datetime
import os

from national_statistics.my_log import logger

DB_FILE = os.path.join(os.path.dirname(__file__), "zxfb.txt")
# print(DB_FILE)


class Recorder(object):
    def __init__(self):
        self.db_file = DB_FILE

    def insert(self, dt_str: str):
        logger.info("保存爬取最近时间成功 {}".format(dt_str))
        with open(self.db_file, "w") as f:
            f.write(dt_str)

    def get(self):
        with open(self.db_file, "r") as f:
            return f.read()


if __name__ == "__main__":
    d = Recorder()
    # d.insert("2020-01-02")
    ret = d.get()
    print(ret == '', type(ret))
    # ret = datetime.datetime.strptime(ret, "%Y-%m-%d")
    # print(ret, type(ret))
