import json
import pprint
import sys
from urllib.request import urlretrieve

import requests


class DetailSpider(object):

    def __init__(self):
        # self.web_url = 'http://www.sse.com.cn/market/othersdata/margin/detail/'
        # self.base_url = 'http://query.sse.com.cn/marketdata/tradedata/queryMargin.do?'
        # self.headers = {
        #     'Accept': '*/*',
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        #     'Cache-Control': 'no-cache',
        #     'Connection': 'keep-alive',
        #     'Cookie': 'yfx_c_g_u_id_10000042=_ck20020212032112531630665331275; yfx_f_l_v_t_10000042=f_t_1580616201243__r_t_1588733126171__v_t_1588748556929__r_c_13; VISITED_MENU=%5B%228740%22%2C%228739%22%2C%228738%22%2C%228726%22%2C%228814%22%2C%229807%22%2C%228811%22%2C%228815%22%2C%228431%22%2C%228817%22%2C%229808%22%5D; JSESSIONID=F8646326AE9A365143DC36078771553B',
        #     'Host': 'query.sse.com.cn',
        #     'Pragma': 'no-cache',
        #     'Referer': 'http://www.sse.com.cn/market/othersdata/margin/detail/',
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
        # }
        self.csv_url = 'http://www.sse.com.cn/market/dealingdata/overview/margin/a/rzrqjygk{}.xls'

    # def get_params(self):
    #     params = {
    #         'jsonCallBack': 'jsonpCallback44175',
    #         'isPagination': 'true',
    #         'tabType': 'mxtype',
    #         'detailsDate': 20200428,
    #         'stockCode': '',
    #         'beginDate': '',
    #         'endDate': '',
    #         'pageHelp.pageSize': 25,
    #         'pageHelp.pageCount': 50,
    #         'pageHelp.pageNo': 1,
    #         'pageHelp.beginPage': 1,
    #         'pageHelp.cacheSize': 1,
    #         'pageHelp.endPage': 6,
    #         '_': 1588748557475,
    #     }
    #     return params
    #
    # def parse_page(self):
    #     resp = requests.get(self.base_url, headers=self.headers, data=self.get_params())
    #     if resp.status_code == 200:
    #         ret = resp.text
    #         datas = json.loads(ret)
    #         print(pprint.pformat(datas))

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