import datetime
import json
import random
import re
import string
import time
from urllib.parse import urlencode
import requests as req
from gne import GeneralNewsExtractor
from base import SpiderBase


class CNStock(SpiderBase):
    def __init__(self):
        super(CNStock, self).__init__()
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
                   "Referer": "http://news.cnstock.com/news/sns_yw/index.html",
                   }
        self.headers = headers
        self.list_url = "http://app.cnstock.com/api/waterfall?"
        self.extractor = GeneralNewsExtractor()
        self.table_name = "cn_stock"
        self.topic_list = [
            'qmt-sns_yw',     # 要闻-宏观
            'qmt-sns_jg',     # 要闻-金融
            "qmt-scp_gsxw",   # 公司-公司聚焦
            "qmt-tjd_ggkx",    # 公司-公告快讯
            "qmt-tjd_bbdj",    # 公司-公告解读
            "qmt-smk_gszbs",    # 市场-直播
            "qmt-sx_xgjj",    # 市场-新股-新股聚焦
            "qmt-sx_zcdt",    # 市场-新股-政策动态
            "qmt-sx_xgcl",    # 市场-新股-新股策略
            "qmt-sx_ipopl",    # 市场-新股-IPO评论
            "qmt-smk_jjdx",    # 市场-基金
            "qmt-sns_qy",    # 市场-券业
            "qmt-smk_zq",    # 市场-债券
            "qmt-smk_xt",    # 市场-信托
            "qmt-skc_tt",    # 科创板-要闻
            "qmt-skc_jgfx",    # 科创板-监管
            "qmt-skc_sbgsdt",    # 科创板-公司
            "qmt-skc_tzzn",    # 科创板-投资
            "qmt-skc_gd",    # 科创板-观点
            "qmt-sjrz_yw",   # 新三板-要闻
        ]
        self.fields = ['pub_date', 'title', 'link', 'article']
        self.name = '宏观等'

    def make_query_params(self, topic, page):
        """
        拼接动态请求参数
        """
        query_params = {
            'colunm': topic,
            'page': str(page),   # 最大 50 页
            'num': str(10),
            'showstock': str(0),
            'callback': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 20)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def _create_table(self):
        self._spider_init()
        sql = '''
          CREATE TABLE IF NOT EXISTS `{}` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `pub_date` datetime NOT NULL COMMENT '发布时间',
            `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
            `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
            `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
            `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
            `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`),
            UNIQUE KEY `link` (`link`),
            KEY `pub_date` (`pub_date`),
            KEY `update_time` (`UPDATETIMEJZ`)
          ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上海证券报'; 
          '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def get_list(self, topic, page):
        params = self.make_query_params(topic, page)
        url = self.list_url + urlencode(params)
        ret = req.get(url, headers=self.headers).text
        json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
        py_data = json.loads(json_data)
        datas = py_data.get("data", {}).get("item")
        if not datas:
            return []
        items = []
        for one in datas:
            item = dict()
            pub_date = datetime.datetime.strptime(one.get("time"), "%Y-%m-%d %H:%M:%S")
            item['pub_date'] = pub_date
            item['title'] = one.get("title")
            link = one.get("link")
            item['link'] = link
            article = self.get_detail(link)
            if article:
                item['article'] = article
                print(item)
                items.append(item)
        return items

    def get_detail(self, detail_url):
        try:
            page = req.get(detail_url, headers=self.headers).text
            result = self.extractor.extract(page)
            content = result.get("content")
            return content
        except:
            return None

    def start(self):
        self._create_table()
        self._spider_init()
        for topic in self.topic_list:
            print(topic)
            topic_items = []
            for page in range(1, 10):
                page_items = self.get_list(topic, page)
                topic_items.extend(page_items)
            print(f"主题 {topic} 爬取数: {len(topic_items)}")
            ret = self._batch_save(self.spider_client, topic_items, self.table_name, self.fields)
            print(f"入库数: {ret}")


if __name__ == "__main__":
    cns = CNStock()
    # 测试解析详情页可以实现自动翻页
    # ret = cns.get_detail("http://ggjd.cnstock.com/company/scp_ggjd/tjd_ggjj/202002/4489878.htm")
    # print(ret)
    cns.start()
