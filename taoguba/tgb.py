import json
import logging
import re
import sys
import time
import traceback
from urllib.parse import urlencode

import pymongo
import pymysql
import requests
from bs4 import BeautifulSoup
from lxml import html

import sys
sys.path.append("./../")

from taoguba.configs import DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB

logger = logging.getLogger()


class BaseSpider(object):
    """
    主要是与抓取逻辑无关的配置项以及与数据库交互的操作
    """
    @property
    def keys(self):   # {'300150.XSHE': '世纪瑞尔',
        """
        从 datacanter.const_secumain 数据库中获取当天需要爬取的股票信息
        返回的是 股票代码: 中文名简称 的字典的形式
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            logger.warning(f"connect [datacenter.const_secumain] to get secucode info today fail, {e}")
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
        in (select distinct SecuCode from const_secumain);""")
        keys = {r[0]: r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return keys

    def convert_lower(self, order_book_id: str):
        """
        转换合约代码为前缀模式 并且前缀字母小写
        :param order_book_id:
        :return:
        """
        EXCHANGE_DICT = {
            "XSHG": "SH",
            "XSHE": "SZ",
            "INDX": "IX",

            "XSGE": "SF",
            "XDCE": "DF",
            "XZCE": "ZF",
            "CCFX": "CF",
            "XINE": "IF",
        }

        code, exchange = order_book_id.split('.')
        ex = EXCHANGE_DICT.get(exchange)
        return ''.join((ex, code)).lower()

    @property
    def lowerkeys(self):  # {sz000651: "格力电器", ...}
        """
        将数据库中查询出的股票代码转换为可用于 url 查询的小写前缀模式
        :return:
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            logger.warning(f"connect [datacenter.const_secumain] to get secucode info today fail, {e}")
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
                   in (select distinct SecuCode from const_secumain);""")

        keys = {self.convert_lower(r[0]): r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return keys


if __name__ == "__main__":
    b = BaseSpider()
    print(b.keys)

    print()

    print(b.lowerkeys)
    sys.exit(0)


class TaogubaSpider(object):
    def __init__(self):
        # 淘股吧的起始爬取的列表页
        self.list_url = "https://www.taoguba.com.cn/quotes/getStockUpToDate?"
        # 每次请求返回的个数 不要设置太大 对对方服务器造成太大压力
        self.perPageNum = 100
        # 因数据量比较大 将数据存入 mongo 数据库中 或者是在测试时使用
        self.mon = pymongo.MongoClient("127.0.0.1:27018").pach.taoguba

    def make_query_params(self, code, timestamp):
        """
        拼接请求参数
        :param code:
        :param timestamp:
        :return:
        """
        query_params = {
            'stockCode': code,  # 查询股票代码
            'actionDate': timestamp,  # 只会按照数量返回这个时间戳之前的数据
            'perPageNum': self.perPageNum,  # 每次请求返回的个数
            "isOpen": "false",  # 不知道干嘛的一个参数 w(ﾟДﾟ)w
        }
        return query_params

    def start_requests(self):
        demo_keys = {
            # 'sz000651': '格力电器', 'sz002051': '中工国际', 'sz002052': '同洲电子',
            'sh601001': '大同煤业', 'sh601988': '中国银行', 'sz002054': '德美化工',
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

    def parse_list(self, code, name, url):
        response = requests.get(url)
        if response.status_code == 200:
            records = json.loads(response.text).get("dto", {}).get("record")
            if records:
                for record in records:
                    #  如果是原文的话这里是 None
                    #  转评的话 这里是有内容的 爬取规则是只要原文 不要转评
                    #  同时 原文的 rtype' 是 'T', 转评的  'rtype'是 'R'
                    if record.get("tops") and record.get("rtype") == "R":
                        logger.info("此内容为转评, 略去")
                        continue

                    article_url = "https://www.taoguba.com.cn/Article/" + str(record.get("rID")) + "/1"
                    item = {}
                    item['stockCode'] = code
                    item['ChiNameAbbr'] = name
                    item["actionDate"] = record.get("actionDate")   # 文章发布时间
                    item['body'] = record.get("body")  # 文章摘要
                    item['subject'] = record.get("subject")  # 文章标题
                    item['userName'] = record.get("userName")  # 用户名 即消息来源
                    item['gnName'] = record.get("gnName")   # 文章谈及概念   TODO list 和 dict 在入库之前再处理
                    item['stockAttr'] = record.get("stockAttr")   # 文章谈及股票
                    # article_url = "https://www.taoguba.com.cn/Article/" + str(record.get("rID")) + "/1"
                    item['articleUrl'] = article_url
                    # 增加一个方便翻页的参数
                    item['rID'] = record.get("rID")
                    print(item)
                    try:
                        self.mon.insert_one(item)
                    except pymongo.errors.DuplicateKeyError:
                        logger.warning("重复插入数据 {}".format(item['articleUrl']))
                    except Exception:
                        traceback.print_exc()

                # 生成下一次爬取的 url 相当于翻页
                more_timestamp = records[-1].get("actionDate")
                more_url = self.list_url + urlencode(self.make_query_params(code, more_timestamp))
                self.parse_list(code, name, more_url)
        else:
            print(url)
            print("股票{}的列表页已经全部入库了".format(name))


if __name__ == "__main__":
    t = TaogubaSpider()
    # 随机映射一个数据卷
    # docker run -p 27018:27017 -v :/data/db --name docker_mongodb -d mongo
    # 指定映射的数据卷
    # docker run -p 27018:27017 -v /Users/furuiyang/gitzip/JustSimpleSpider/taoguba/mongodb:/data/db --name docker_mongodb -d mongo
    # t.mon.insert_one({"name": "ruiyang"})
    # print(t.mon.find({"name": "ruiyang"}).next())
    # print(t.mon.delete_one({"name": "ruiyang"}))
    # 为该数据库设置唯一索引
    # db.price.ensureIndex({"code": 1, "time": 1}, {unique: true})
    # create_index([('x',1)], unique = True, background = True)
    # t.mon.ensure_index([("stockCode", 1), ("articleUrl", 1)], unique=True)
    # 进入交互模式的终端 这样即可对数据库进行 cli 操作
    # docker exec -it 5034b446  mongo admin


    t.start_requests()
    pass

    # def _parse_page(self, body):
    #     """
    #     对文章详情页面进行解析
    #     """
    #     # TODO 详情页的页数 1-n
    #     s_html = re.findall(r"<!-- 主贴内容开始 -->(.*?)<!-- 主贴内容结束 -->", body, re.S | re.M)[0]
    #     soup = BeautifulSoup(s_html, 'lxml')
    #     # 因为是要求文章中的图片被替换为链接放在相对应的位置所以这样子搞了w(ﾟДﾟ)w 之后看看有啥更好的办法
    #     imgs = soup.find_all(attrs={'data-type': 'contentImage'})
    #     if imgs:
    #         urls = [img['data-original'] for img in imgs]
    #         s_imgs = re.findall(r"<img.*?/>", s_html)  # 非贪婪匹配
    #         match_info = dict(zip(s_imgs, urls))
    #         for s_img in s_imgs:
    #             s_html = s_html.replace(s_img, match_info.get(s_img))
    #         # 替换之后再重新构建一次 这时候用 text 就直接拿到了 url ^_^
    #         soup = BeautifulSoup(s_html, 'lxml')
    #     text = soup.div.text.strip()
    #     return text

    # def _parse_page_num(self, page):
    #     doc = html.fromstring(page)
    #     page_num = doc.xpath("//div[@class='t_page right fy_pd3']/div[@class='left t_page01']")
    #     page_str = page_num[0].text_content()  # 末页下一页上一页首页共1/1页
    #     page_now, page_all = re.findall("共(.+)/(.+)页", page_str)[0]
    #     return page_now, page_all

    # def parse_detail(self, response):
    #     if response.status == 200:
    #         body = response.text
    #         # 获取当前页的内容
    #         content = self._parse_page(body)
    #         logger.info(f"已经获取到当前页面的内容啦: --> {content[:10]}")
    #         # 判断当前页是否是最终页
    #         page_now, page_all = self._parse_page_num(body)
    #         if page_all == "1" and page_now == page_all:
    #             logger.info("文章仅一页")
    #             # 按照正常的流程返回 item
    #             meta = copy.deepcopy(response.request.meta)
    #             item = meta.get("item")
    #             item["articleContent"] = content
    #             # print("------> ", item.get("actionDate"))
    #             # print(item.get("stockCode"), item.get("ChiNameAbbr"), item.get("subject"), type(item.get("stockCode")))
    #             yield item
    #         elif page_now == page_all:
    #             logger.info("已到达文章总页数的最后一页")
    #             # 已经到达预设的最后一页
    #             meta = copy.deepcopy(response.request.meta)
    #             item = meta.get("item")
    #             content_dict = item.get("articleContent", {})
    #             content_dict[page_now] = content
    #             # 将每一页的 content 拼接起来
    #             item["articleContent"] = "\r\n".join(content_dict.values())
    #             # item.update({"articleContent": content_dict})
    #             yield item
    #         else:
    #             # 假如是 1 和 n 的情况
    #             logger.info(f"爬取文章的第 {page_now} / {page_all} 页")
    #             meta = copy.deepcopy(response.request.meta)
    #             item = meta.get("item")
    #             content_dict = item.get("articleContent", {})
    #             content_dict[page_now] = content
    #             item.update({"articleContent": content_dict})
    #             # 拼接下一页请求的 url
    #             next_url = "https://www.taoguba.com.cn/Article/" + str(item["rID"]) + "/" + str(int(page_now) + 1)
    #             yield scrapy.Request(
    #                 next_url,
    #                 callback=self.parse_detail,
    #                 meta=meta,
    #             )