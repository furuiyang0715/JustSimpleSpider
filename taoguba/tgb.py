import json
import logging
import re
import time
import traceback
from urllib.parse import urlencode
import pymongo
import requests
from bs4 import BeautifulSoup
from lxml import html
import sys

sys.path.append("./../")
from taoguba.dc_base import DCSpider
from taoguba.proxy_spider import ProxySpider
from taoguba.common.proxy_tools.proxy_pool import QueueProxyPool

logger = logging.getLogger()


class TaogubaSpider(DCSpider, ProxySpider):
    def __init__(self):
        # 淘股吧的起始爬取的列表页
        self.list_url = "https://www.taoguba.com.cn/quotes/getStockUpToDate?"
        # 每次请求返回的个数 不要设置太大 对对方服务器造成太大压力
        self.perPageNum = 100
        # 因数据量比较大 将数据存入 mongo 数据库中 或者是在测试时使用
        self.mon = pymongo.MongoClient("127.0.0.1:27018").pach.taoguba
        self.ip_pool = QueueProxyPool()

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
                    print("开始解析详情页 {}".format(detail_link))
                    content = self.parse_detail(item)
                    print(item['stockCode'], "------> ", content[:100])
                    print()
                except:
                    print("解析详情页失败 ")

    def _parse_page(self, url):
        """
        对文章详情页面进行解析
        """
        body = self.get(url).text
        # TODO 详情页的页数 1-n
        s_html = re.findall(r"<!-- 主贴内容开始 -->(.*?)<!-- 主贴内容结束 -->", body, re.S | re.M)[0]
        soup = BeautifulSoup(s_html, 'lxml')
        # 因为是要求文章中的图片被替换为链接放在相对应的位置所以这样子搞了w(ﾟДﾟ)w 之后看看有啥更好的办法
        imgs = soup.find_all(attrs={'data-type': 'contentImage'})
        if imgs:
            urls = [img['data-original'] for img in imgs]
            s_imgs = re.findall(r"<img.*?/>", s_html)  # 非贪婪匹配
            match_info = dict(zip(s_imgs, urls))
            for s_img in s_imgs:
                s_html = s_html.replace(s_img, match_info.get(s_img))
            # 替换之后再重新构建一次 这时候用 text 就直接拿到了 url ^_^
            soup = BeautifulSoup(s_html, 'lxml')
        text = soup.div.text.strip()
        return text

    def _parse_page_num(self, url):
        """
        判断当前的文章详情页文章一共分几页
        :param page:
        :return:
        """
        page = self.get(url).text
        doc = html.fromstring(page)
        page_num = doc.xpath("//div[@class='t_page right fy_pd3']/div[@class='left t_page01']")
        page_str = page_num[0].text_content()  # 末页下一页上一页首页共1/1页
        page_now, page_all = re.findall("共(.+)/(.+)页", page_str)[0]
        return page_now, page_all

    def parse_detail(self, item):
        durl = item['articleUrl']
        status_code = self.get(durl).status_code
        if status_code == 200:
            page_now, page_all = self._parse_page_num(durl)
            print(page_now, "===> ", page_all)
            # 文章仅一页
            if page_all == "1" and page_now == page_all:
                print("文章仅一页")
                content = self._parse_page(durl)
                print(f"已经获取到当前页面的内容啦: --> {content[:10]}")
                return content

            # 一次爬取每一页再拼接起来
            else:
                content_dict = {}
                while int(page_now) <= int(page_all):
                    print(f"开始爬取文章的第 {page_now} / {page_all} 页")
                    url = "https://www.taoguba.com.cn/Article/" + str(item["rID"]) + "/" + page_now
                    content_dict[page_now] = self._parse_page(url)
                    print(content_dict[page_now][:10])
                    page_now = str(int(page_now) + 1)
                return "\r\n".join(content_dict.values())
        elif status_code == 403:
            print("详情页被反爬")
            pass

    def start_requests(self):
        demo_keys = {
            # 'sz000651': '格力电器', 'sz002051': '中工国际', 'sz002052': '同洲电子',
            # 'sh601001': '大同煤业', 'sh601988': '中国银行', 'sz002054': '德美化工',
            # 'sz002055': '得润电子', 'sz002056': '横店东磁', 'sh600048': '保利发展',
            'sz002057': '中钢天源', 'sz002058': '威尔泰', 'sz002059': '云南旅游',

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
            else:   # 说明该数据已经爬取完毕了
                print('结束的url是{}'.format(url))
                print("股票{}的列表页已经全部入库了".format(name))
        else:
            # 请求结果的状态码不是 200 记录一下
            print("{} 请求异常， 异常 url 是{}".format(code, url))


if __name__ == "__main__":
    t = TaogubaSpider()
    # 为该数据库设置唯一索引
    # db.price.ensureIndex({"code": 1, "time": 1}, {unique: true})
    # create_index([('x',1)], unique = True, background = True)
    # t.mon.ensure_index([("stockCode", 1), ("articleUrl", 1)], unique=True)
    # 进入交互模式的终端 这样即可对数据库进行 cli 操作
    # docker exec -it 5034b446  mongo admin

    # t.start_requests()

    # url = "https://www.taoguba.com.cn/Article/1006998/1"
    # t.get(url)
    # ret = t._parse_page_num(url)
    # print(ret)
    # ret2 = t._parse_page(url)
    # print(ret2)

    t.select_topic_from_mongo("sz002059")