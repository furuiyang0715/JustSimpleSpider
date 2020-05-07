import json
import logging
import pprint
import sys
from urllib.request import urlretrieve
import requests
import xlrd

from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DetailSpider(MarginBase):
    def __init__(self):
        self.csv_url = 'http://www.sse.com.cn/market/dealingdata/overview/margin/a/rzrqjygk{}.xls'
        self.inner_code_map = self.get_inner_code_map()

    def get_inner_code_map(self):
        """
        获取聚源内部编码映射表
        https://dd.gildata.com/#/tableShow/27/column///
        https://dd.gildata.com/#/tableShow/718/column///
        """
        juyuan = self._init_pool(self.juyuan_cfg)
        # 8 是开放式基金
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8) and SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        ret = juyuan.select_all(sql)
        juyuan.dispose()
        info = {}
        for r in ret:
            key = r.get("SecuCode")
            value = r.get('InnerCode')
            info[key] = value
        return info

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

    def load_xls(self):
        dt = 20200506
        url = self.csv_url.format(dt)
        urlretrieve(url, "./data_dir/{}.xls".format(dt), self.callbackfunc)

    def get_inner_code(self, secu_code):
        ret = self.inner_code_map.get(secu_code)
        if not ret:
            logger.warning("{} 不存在内部编码".format(secu_code))
            raise
        return ret

    def start(self):
        # 打开已有的工作薄
        wb = xlrd.open_workbook('./data_dir/20200506.xls')
        # 明细信息表单
        detail = wb.sheet_by_name("明细信息")
        # 总数据量
        rows = detail.nrows - 1
        # 表头信息
        heads = detail.row_values(0)
        # print(heads)
        # ['标的证券代码', '标的证券简称', '本日融资余额(元)', '本日融资买入额(元)', '本日融资偿还额(元)', '本日融券余量', '本日融券卖出量', '本日融券偿还量']
        # | id | SecuMarket | InnerCode | SecuCode | SecuAbbr | SerialNumber | ListDate            | TargetCategory | CREATETIMEJZ        | UPDATETIMEJZ
        # 数据
        datas = []
        for i in range(1, rows+1):
            data = detail.row_values(i)
            datas.append(self.get_inner_code(data[0]))

        print(datas)


if __name__ == "__main__":
    DetailSpider().start()
