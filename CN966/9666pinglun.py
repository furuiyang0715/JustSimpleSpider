import datetime
import re

import requests
from lxml import html

from base import SpiderBase


class PingLun9666(SpiderBase):
    def __init__(self):
        super(PingLun9666, self).__init__()
        self.web_url = 'http://pinglun.9666.cn/zaowanping/'  # 早晚评
        self.web_url2 = 'http://pinglun.9666.cn/shaizhanji/'  # 热点追踪
        self.author_url = 'http://pinglun.9666.cn/zhuanlan/'   # 专栏
        self.format_url = 'http://pinglun.9666.cn/zaowanping/?pager.offset=15&pageNo={}&pageSize=15'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            'Cookie': 'cowboy_website=2a1644a5-0b40-4d46-93ca-367c54e39220; cowboy_visit_time=1595899251676; Hm_lvt_94656c824ef4eacf1a61cd662f7a7f17=1595899253; __utmc=236883550; __utmz=236883550.1595899253.1.1.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; cowboy_login=C3AD5319C3B607C2840F46C286C3AEC2B9C393C2AD3D3060C2896512423AC3B7C3B1596E2B47C282C3A21145C28C3E41C395C393C390C2A7C38B; cowboy_login_imply=C3AD5319C3B607C2840F46C286C3AEC2B9C393C2AD3D3060C2896512423AC3B7C3B1596E2B47C282C3A21145C28C3E41C395C393C390C2A7C38B; cowboy_nick_name=e882a1e58f8b343838393937; cowboy_user_name=nz_d09e0490; cowboy_latest_login_time=1595899414; Hm_lvt_11beb42de0d3859b0af4fd1b6f3b45cf=1595899267,1595899423,1595899565; Hm_lpvt_94656c824ef4eacf1a61cd662f7a7f17=1595902758; Hm_lpvt_11beb42de0d3859b0af4fd1b6f3b45cf=1595902758; __utma=236883550.1639834052.1595899253.1595899253.1595902758.2; __utmt=1; __utmb=236883550.2.9.1595902758; JSESSIONID=DBE042153E24D84C8E659A9DFDB824ED',
        }
        self.table_name = '9666pinglun'
        self.name = '牛仔网评论'
        self.fields = ['pub_date', 'title', 'article', 'link']

    def _create_table(self):
        sql = '''
        CREATE TABLE  IF NOT EXISTS `{}` (
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{}'; 
        '''.format(self.table_name, self.name)
        self._spider_init()
        self.spider_client.insert(sql)
        self.spider_client.end()

    def get_detail(self, url):
        resp = requests.get(url, headers=self.headers)
        if resp and resp.status_code == 200:
            body = resp.text
            doc = html.fromstring(body)
            article = doc.xpath("//div[@class='blog-article']")
            if article:
                article = article[0].text_content()
                article = self._process_content(article)
                return article

    def get_list(self, url):
        resp = requests.get(url, headers=self.headers)
        if resp and resp.status_code == 200:
            body = resp.text
            doc = html.fromstring(body)
            news_list = doc.xpath(".//div[@id='hotspot_list_box']")
            if news_list:
                news_list = news_list[0]
                boxs1 = news_list.xpath(".//div[@class='channel  clearfix list-box']")
                boxs2 = news_list.xpath(".//div[@class='channel clearfix list-box']")
                boxs1.extend(boxs2)
                for box in boxs1:
                    info = box.xpath(".//div[@class='channel_one']/span[@class='f24 fb']/a")[0]
                    link = info.xpath("./@href")[0]
                    article = self.get_detail(link)
                    if article:
                        title = info.text_content()
                        pub_str = box.xpath(".//p[@class='list-info gray01']")[0]
                        pub_str = pub_str.text_content().strip()
                        pub_date = re.findall("\d{2}-\d{2} \d{2}:\d{2}", pub_str)[0]
                        pub_date = str(datetime.datetime.now().year) + "-" + pub_date
                        item = dict()
                        item['link'] = link
                        item['title'] = title
                        item['pub_date'] = pub_date
                        item['article'] = article
                        self._save(self.spider_client, item, self.table_name, self.fields)

    def get_authors(self):
        resp = requests.get(self.author_url, headers=self.headers)
        if resp and resp.status_code == 200:
            body = resp.text
            doc = html.fromstring(body)
            ret = doc.xpath(".//div[@class='box']/ul[@class='list list02']")[0]
            links = ret.xpath(".//li/h3/a/@href")
            return links

    def get_zhuanlan(self, url):
        resp = requests.get(url, headers=self.headers)
        if resp and resp.status_code == 200:
            body = resp.text
            doc = html.fromstring(body)
            boxs = doc.xpath(".//div[@class='article mt64']")
            if boxs:
                boxs = boxs[0]
                boxs = boxs.xpath(".//div[@class='channel pb32 clearfix mt48']")
                if boxs:
                    for box in boxs:
                        info = box.xpath(".//h2[@class='f24 fb']/a")[0]
                        title = info.text_content()
                        link = info.xpath("./@href")[0]
                        article = self.get_detail(link)
                        if article:
                            pub_str = box.xpath(".//p[@class='list-info gray01']")[0]
                            pub_str = pub_str.text_content().strip()
                            pub_date = re.findall("\d{2}-\d{2} \d{2}:\d{2}", pub_str)[0]
                            pub_date = str(datetime.datetime.now().year) + "-" + pub_date
                            item = dict()
                            item['link'] = link
                            item['title'] = title
                            item['pub_date'] = pub_date
                            item['article'] = article
                            self._save(self.spider_client, item, self.table_name, self.fields)

    def start(self):
        self._create_table()

        # 爬取早晚评
        for page_num in range(1, 3):
            url = self.format_url.format(page_num)
            self.get_list(url)

        # 爬取热点追踪
        self.get_list(self.web_url2)

        # 爬取专栏作者
        zhuanlan_links = self.get_authors()
        if zhuanlan_links:
            for zlink in zhuanlan_links:
                print(zlink)
                self.get_zhuanlan(zlink)


if __name__ == "__main__":
    PingLun9666().start()
