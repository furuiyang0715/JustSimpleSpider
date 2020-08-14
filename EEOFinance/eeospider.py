import datetime
import json
import re
import sys
import time

import requests
from lxml import html

from base import SpiderBase


class EEOSpider(SpiderBase):
    """经济观察网"""
    def __init__(self):
        super(EEOSpider, self).__init__()
        # 起始首页链接
        self.index_url = 'http://www.eeo.com.cn/'
        # 需要爬取的分逻辑
        self.topic_words = [
            'shangyechanye',  # 商业产业
            'caijing',        # 财经
            'dichan',         # 地产
            'qiche',          # 汽车
            'tmt',            # tmt
            'pinglun',        # 评论
            'yanjiuyuan',     # 研究院
        ]
        self.topic_format_url = 'http://www.eeo.com.cn/{}/'
        self.api_format_url = 'http://app.eeo.com.cn/?app=wxmember&controller=index&action=getMoreArticle\
&jsoncallback=jsonp{}\
&catid=%s\
&allcid=%s\
&page=0\
&_={}'.format(int(time.time() * 1000), int(time.time() * 1000))
        self.topic_urls = [self.topic_format_url.format(topic) for topic in self.topic_words]
        # 主题与代码类别编号的对应关系
        self.topic_code_map = {
            'shangyechanye': {"catid": '3572', 'allcid': '397442,397434,397412,397399,397393,397282,397264,397222,397116,397115,397015,397011,397008,397007,397006,397013'},
            'caijing': {"catid": '3548', 'allcid': '399177,399154,399124,399092,399076,399077,399071,399018,398686,398574,398450,398445,398374,398167,398165,398106'},
            'dichan': {"catid": '3583', 'allcid': '399218,399108,399085,398868,398630,398628,398561,398355,398341,398534,398380,398470,398465,398381,398405,398370'},
            'qiche': {"catid": '3559', 'allcid': '399414,399388,398657,398623,398621,398611,398479,398349,398231,398227,397935,397847,397684,397523,397259,397207'},
            'tmt': {"catid": '3549', 'allcid': '399341,399316,399310,399192,399103,399064,399047,399040,399028,398919,398894,398891,398872,398678,398676,397930'},
            'pinglun': {"catid": '3550', 'allcid': '399073,399036,398817,397910,397659,397653,397648,397632,397534,397519,397440,397436,396928,396772,396765,396514'},
            'yanjiuyuan': {"catid": '3674', 'allcid': '398618,398542,397159,396650,396662,396670,396467,395563,394953,394936,394658,394168,393817,393775,393772,393617'},
        }
        # print(self.api_format_url % ("hello", 'world'))

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'PHPSESSID=7avdv48orrl42d4s323eae4dn5; acw_tc=2760775215970417166888855e8f887a018cbf5f73aab22ec8d9ae03f7e2b4; SERVERID=adeed77a8e607bd6b1d16fea05016e81|1597041716|1597041716',
            # 'Host': 'www.eeo.com.cn',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        }
        self.table_name = 'EEONews'
        self.name = '经济观察网新闻'
        self.fields = ['pub_date', 'title', 'link', 'article', 'author']

    def get_topic(self, url):
        """获取栏目资讯"""
        resp = requests.get(url, headers=self.headers)
        if resp and resp.status_code == 200:
            text = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(text)
            articles = doc.xpath(".//div[@class='list']/ul[@id='lyp_article']/li")
            items = []
            for article in articles:
                link = article.xpath("./a/@href")[0]   # 文章链接
                title = article.xpath(".//p")[0].text_content()    # 文章标题

                if len(title) > 64:
                    title = title[:64]

                ret = self.get_detail(link)

                if not ret:
                    continue

                elif isinstance(ret, str):
                    item = {
                        'link': link,
                        'title': title,
                        'article': ret,
                    }

                else:   # isinstance(ret, tuple):
                    item = {
                        'link': link,
                        'title': title,
                        'author': ret[0],
                        'pub_date': ret[1],
                        'article': ret[2],
                    }
                print(item)
                items.append(item)
            return items
        return None

    def get_detail(self, url, is_api=False):
        resp = requests.get(url, headers=self.headers)
        if resp and resp.status_code == 200:
            body = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(body)
            try:
                article = doc.xpath(".//div[@class='xx_boxsing']")[0]
                article = article.text_content()
            except:
                article = ''

            if is_api:
                return article

            else:
                try:
                    head_part = doc.xpath(".//div[@class='xd-b-b']")[0]
                    pub_info = head_part.xpath("./p")[0]
                    pub_info = pub_info.text_content()
                    pub_date = re.findall(r"\d{4}-\d{2}-\d{2}", pub_info)[0]  # 匹配出时间
                    pub_date = pub_date.strip()
                    pub_date = datetime.datetime.strptime(pub_date, "%Y-%m-%d")
                    author = re.findall(r'[\u4e00-\u9fa5]+', pub_info)[0]  # 匹配出作者
                except:
                    return
                else:
                    if isinstance(pub_date, datetime.datetime):
                        return author, pub_date, article

    def parse_api(self, api_url):
        print(api_url)
        resp = requests.get(api_url, headers=self.headers)
        if resp and resp.status_code == 200:
            body = resp.text
            body = body.encode("ISO-8859-1").decode("utf-8")
            data_str = re.findall('jsonp\d{13}\((.*)\)', body)[0]
            try:
                datas = json.loads(data_str)
            except:
                return

            articles = datas.get("article")
            items = []
            for one in articles:
                item = {}
                pub_ts = int(one.get("published"))
                pub_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pub_ts))
                item['pub_date'] = pub_date
                title = one.get("title")
                if len(title) > 64:
                    title = title[:64]
                item['title'] = title
                item['author'] = one.get("author")
                link = one.get("url")
                item['link'] = link
                article = self.get_detail(link, is_api=True)
                item['article'] = article
                print(item)
                items.append(item)
            return items

    def create_table(self):
        self._spider_init()
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `author` varchar(10) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章作者',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT = '{}';  
        '''.format(self.table_name, self.name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def start(self):
        # 建表
        self.create_table()

        # 网页解析部分
        for url in self.topic_urls:
            topic_index_items = self.get_topic(url)
            if topic_index_items and isinstance(topic_index_items, list):
                # print("in")
                ret = self._batch_save(self.spider_client, topic_index_items, self.table_name, self.fields)
                print(ret)

        # api 部分
        for topic in self.topic_words:
            cat_info = self.topic_code_map.get(topic)
            api_url = self.api_format_url % (cat_info.get("catid"), cat_info.get('allcid'))
            api_topic_items = self.parse_api(api_url)
            if api_topic_items and isinstance(api_topic_items, list):
                ret = self._batch_save(self.spider_client, api_topic_items, self.table_name, self.fields)


if __name__ == '__main__':
    eeo = EEOSpider()
    eeo.start()
