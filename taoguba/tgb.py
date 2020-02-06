import logging
import time
import traceback
from urllib.parse import urlencode
import pymongo

import sys
sys.path.append("./../")
from taoguba.parse_tools import ParseSpider
from taoguba.dc_base import DCSpider
from taoguba.proxy_spider import ProxySpider
from taoguba.common.proxy_tools.proxy_pool import QueueProxyPool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TaogubaSpider(DCSpider, ProxySpider, ParseSpider):
    def __init__(self):
        # 淘股吧的起始爬取的列表页
        self.list_url = "https://www.taoguba.com.cn/quotes/getStockUpToDate?"
        # 每次请求返回的个数 不要设置太大 对对方服务器造成太大压力
        self.perPageNum = 100
        # 因数据量比较大 将数据存入 mongo 数据库中 或者是在测试时使用
        self.mon = pymongo.MongoClient("127.0.0.1:27018").pach.taoguba
        self.ip_pool = QueueProxyPool()
        self.error_detail = []
        self.error_list = []

    def insert_list_info(self, item):
        try:
            self.mon.insert_one(item)
        except pymongo.errors.DuplicateKeyError:
            logger.warning("重复插入数据 {}".format(item['articleUrl']))
        except Exception:
            traceback.print_exc()

    def select_topic_from_mongo(self, code):
        """
        从 mongo 数据库中获取指定股票的待爬取详情
        :param code:
        :return:
        """
        cursor = self.mon.find({"stockCode": code})
        for item in cursor:
            detail_link = item.get("articleUrl")
            if detail_link:
                try:
                    logger.debug("开始解析详情页 {}".format(detail_link))
                    content = self.parse_detail(item)
                    logger.debug(item['stockCode'], "------> ", content[:100])
                except:
                    self.error_detail.append(detail_link)
                    logger.debug("解析详情页失败 ")

    def start_requests(self):
        demo_keys = {
            # 'sz000651': '格力电器', 'sz002051': '中工国际', 'sz002052': '同洲电子',
            # 'sh601001': '大同煤业', 'sh601988': '中国银行', 'sz002054': '德美化工',
            # 'sz002055': '得润电子', 'sz002056': '横店东磁', 'sh600048': '保利发展',
            # 'sz002057': '中钢天源', 'sz002058': '威尔泰', 'sz002059': '云南旅游',
            'sh601006': '大秦铁路', 'sz002060': '二局股份', 'sz002061': '浙江交科'

        }

        for code, name in demo_keys.items():
        # for code, name in self.lowerkeys.items():
            logger.info(f"code: {code}, name: {name}")
            item = {}
            # 股票代码以及中文简称
            item["stockCode"] = code
            item['ChiNameAbbr'] = name
            tstamp = int(time.time()) * 1000  # js 中的时间戳 第一次这个值选用当前时间
            query_params = self.make_query_params(code, tstamp)
            # 拼接出某只股票的起始 url
            start_url = self.list_url + urlencode(query_params)
            logger.info(f"股票 {name} 的起始 url 是 {start_url}")
            self.parse_list(code, name, start_url)


if __name__ == "__main__":
    t = TaogubaSpider()
    # 将全部的列表页 url 采集到 mongodb 数据库中
    t.start_requests()
    # 查看采集是失败的页面
    print('采集失败的详情页是'.format(t.error_detail))
    print('采集失败的列表页是'.format(t.error_list))
    # 采集全部的详情页页面 并将其插入到 mysql 数据库中

    # t.select_topic_from_mongo("sz002059")
