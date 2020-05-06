import json
import pprint
import sys
from urllib.request import urlretrieve
import requests


class DetailSpider(object):
    def __init__(self):
        self.csv_url = 'http://www.sse.com.cn/market/dealingdata/overview/margin/a/rzrqjygk{}.xls'

    def callbackfunc(self, blocknum, blocksize, totalsize):
        """
        回调函数
        :param blocknum: 已经下载的数据块
        :param blocksize:  数据块的大小
        :param totalsize: 远程文件的大小
        :return:
        """
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        sys.stdout.write("\r%6.2f%%" % percent)
        sys.stdout.flush()

    def start(self):
        dt = 20200430
        url = self.csv_url.format(dt)
        urlretrieve(url, "{}.xls".format(dt), self.callbackfunc)


if __name__ == "__main__":
    DetailSpider().start()
