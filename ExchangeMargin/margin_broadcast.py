import datetime
import json
import os
import random
import sys
import time
from urllib.parse import urljoin

import requests
from lxml import html

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from ExchangeMargin.base import MarginBase, logger


class MarginBroadcast(MarginBase):
    """爬取上交所和深交所的融资融券公告"""
    def __init__(self):
        super(MarginBroadcast, self).__init__()
        self. firelds = ['title', 'link', 'time', 'content', 'keyword']

        # sh
        self.sh_url = 'http://www.sse.com.cn/disclosure/magin/announcement/s_index.htm'
        self.sh_base_url = 'http://www.sse.com.cn/disclosure/magin/announcement/s_index_{}.htm'
        self.dt_format = "%Y-%m-%d"
        self.error_urls = []

        # sz
        self.sz_url = 'http://www.szse.cn/api/search/content?random={}'.format(random.random())
        self.error_pages = []
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '85',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.szse.cn',
            'Origin': 'http://www.szse.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://www.szse.cn/disclosure/margin/business/index.html',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'X-Request-Type': 'ajax',
            'X-Requested-With': 'XMLHttpRequest',
        }

        self.announcement_table = 'margin_announcement'

    def _create_table(self):
        """对公告爬虫建表 """
        # self._spider_init()
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `market` int(11) DEFAULT NULL COMMENT '证券市场',  
          `title` varchar(200) DEFAULT NULL COMMENT '公告标题',
          `link` varchar(200) DEFAULT NULL COMMENT '公告链接',
          `time` datetime NOT NULL COMMENT '公告发布时间', 
          `content` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '公告内容',
          `keyword` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '公告关键词',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `un2` (`market`, `link`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='交易所融资融券公告信息';
        
        '''.format(self.announcement_table)
        self.spider_conn.execute(sql)
        # self.spider_client.insert(sql)
        logger.info("爬虫公告表建表成功")

    def _make_sz_params(self, page_num):
        '''
        keyword:
        time: 0
        range: title
        channelCode[]: business_news
        currentPage: 1
        pageSize: 20
        '''
        datas = {
            "keyword": '',
            'time': '',
            'range': 'title',
            'channelCode[]': 'business_news',
            'currentPage': page_num,
            'pageSize': 20,
        }
        return datas

    def parse_json_content(self, url):
        """eg. http://www.szse.cn/disclosure/notice/general/t20200430_576647.json """
        resp = requests.get(url)
        if resp.status_code == 200:
            ret = resp.text
            py_data = json.loads(ret)
            content = py_data.get("data", {}).get("content", '')
            if content:
                doc = html.fromstring(content)
                content = self._process_content(doc.text_content())
                return content
            return ''

    def trans_dt(self, dt: int):
        """eg. 1588176000000 """
        if not isinstance(dt, int):
            dt = int(dt)
        tl = time.localtime(dt/1000)
        ret = time.strftime("%Y-%m-%d %H:%M:%S", tl)
        return ret

    def sz_start(self):
        self._spider_init()
        for page in range(1, 8):
            logger.info("page is {}".format(page))
            datas = self._make_sz_params(page)
            resp = requests.post(self.sz_url, headers=self.headers, data=datas)
            # print(resp)
            if resp.status_code == 200:
                ret = resp.text
                py_ret = json.loads(ret)
                announcements = py_ret.get("data")
                items = []
                for a in announcements:
                    # print(a)
                    item = dict()
                    item['market'] = 90  # 深交所
                    item['title'] = a.get("doctitle")
                    item['link'] = a.get("docpuburl")
                    item['time'] = self.trans_dt(a.get('docpubtime'))
                    # eg. http://www.szse.cn/disclosure/notice/general/t20200430_576647.json
                    content_json_url = urljoin("http://www.szse.cn", a.get("docpubjsonurl"))
                    content = self.parse_json_content(content_json_url)
                    item['content'] = content
                    items.append(item)
                print(items)
                ret = self._batch_save(self.spider_client, items, self.announcement_table, self.firelds)
            else:
                self.error_pages.append(page)

    def sh_start(self):
        for page in range(1, 23):
            if page == 1:
                url = self.sh_url
            else:
                url = self.sh_base_url.format(page)
            self.post_sh(url)

    def post_sh(self, url):
        self._spider_init()
        resp = requests.post(url)
        if resp.status_code == 200:
            body = resp.text
            try:
                body = body.encode("ISO-8859-1").decode("utf-8")
            except:
                self.error_urls.append(url)
            doc = html.fromstring(body)
            broadcasts = doc.xpath(".//div[@class='sse_list_1 js_createPage']/dl/dd")
            items = []
            for b in broadcasts:
                item = dict()
                item['market'] = 83  # 上交所

                show_dt_str = b.xpath("./span")[0].text_content()
                show_dt = datetime.datetime.strptime(show_dt_str, self.dt_format)
                item['time'] = show_dt

                title = b.xpath("./a")[0].text_content()
                item['title'] = title

                href = b.xpath("./a/@href")[0]
                href = urljoin("http://www.sse.com.cn/", href)
                item['link'] = href

                if href.endswith(".pdf") or href.endswith(".doc"):
                    item['content'] = ''
                    item['keyword'] = ''
                else:
                    ret = self.parse_sh_detail(href)
                    content = ret.get("content")
                    keyword = ret.get("keyword")
                    item['content'] = content
                    item['keyword'] = keyword
                items.append(item)

            print(items)
            ret = self._batch_save(self.spider_client, items, self.announcement_table, self.firelds)

    def parse_sh_detail(self, url):
        """
        eg. http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200430_5085195.shtml
        :param url:
        :return:
        """
        resp = requests.get(url)
        if resp.status_code == 200:
            body = resp.text
            try:
                body = body.encode("ISO-8859-1").decode("utf-8")
            except:
                self.error_urls.append(url)
            doc = html.fromstring(body)
            try:
                # TODO 对 content 进行去噪处理
                content = doc.xpath("//div[@class='allZoom']")[0].text_content()
            except:
                content = ''

            if not content:
                try:
                    content = doc.xpath("//div[@class='article-infor']")[0].text_content()
                except:
                    content = ''

            if content:
                content = self._process_content(content)
            # 提取本篇的关键词
            try:
                key_words = doc.xpath("//span[@id='keywords']")[0].text_content().split()
                words = []
                for word in key_words:
                    word = word.strip(",")
                    words.append(word)
                words_str = ','.join(words)
            except:
                words_str = ''
            return {"content": content, "keyword": words_str}

    def start(self):
        self._create_table()

        self.sh_start()

        self.sz_start()

        logger.info(self.error_urls)
        logger.info(self.error_pages)


def task():
    MarginBroadcast().start()


if __name__ == "__main__":
    task()
