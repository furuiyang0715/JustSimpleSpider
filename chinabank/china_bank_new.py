# -*- coding: utf-8 -*-

import re
import base64
import requests as req
from lxml import html
from chinabank.my_log import logger
from chinabank.configs import MYSQL_TABLE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from chinabank.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline


class ChinaBank(object):
    """
    中国银行爬虫
        爬取两个模块：
        （1） 数据解读
        （2） 新闻发布
    """
    def __init__(self):
        if MYSQL_TABLE == "chinabank_shujujiedu":
            self.url = 'http://www.pbc.gov.cn/diaochatongjisi/116219/116225/11871/index{}.html'
        elif MYSQL_TABLE == "chinabank_xinwenfabu":
            self.url = 'http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index{}.html'
        else:
            raise RuntimeError("请检查数据起始 url")

        self.sql_client = MyPymysqlPool(
            {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
            }
        )

        self.db = MYSQL_DB
        self.table = MYSQL_TABLE
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)
        self.error_list = []
        self.error_pages = []

    def get_refer_url(self, body):
        """获取重定向之后的网址"""
        doc = html.fromstring(body)
        script_content = doc.xpath("//script")[0].text_content()
        re_str = r"var(.+?).split"
        ret = re.findall(re_str, script_content)[0]
        # print("正则结果: ", ret)
        ret = ret.lstrip("|(")
        ret = ret.rstrip("')")
        ret_lst = ret.split("|")
        names = ret_lst[0::2]
        params = ret_lst[1::2]
        info = dict(zip(names, params))
        # print("info is: ")
        # print(pprint.pformat(info))
        factor = sum([ord(ch) for ch in info.get("wzwsquestion")]) * int(info.get("wzwsfactor")) + 0x1b207
        raw = f'WZWS_CONFIRM_PREFIX_LABEL{factor}'
        refer_url = info.get("dynamicurl") + '?wzwschallenge=' + base64.b64encode(raw.encode()).decode()
        return "http://www.pbc.gov.cn" + refer_url

    def get_page(self, url):
        s = req.Session()
        h1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.pbc.gov.cn',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        }
        resp1 = s.get(url, headers=h1)
        # print(resp1)
        cookie1 = resp1.headers.get("Set-Cookie").split(";")[0]
        origin_text = resp1.text
        # print(origin_text)
        redirect_url = self.get_refer_url(origin_text)
        # print(redirect_url)
        h1.update({
            'Cookie': cookie1,
            'Referer': 'http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index1.html',
        })
        resp2 = s.get(redirect_url, headers=h1)
        text = resp2.text.encode("ISO-8859-1").decode("utf-8")
        return text

    def save_to_mysql(self, item):
        self.pool.save_to_database(item)

    def crawl_list(self, offset):
        list_page = self.get_page(self.url.format(offset))
        item_list = self.parse_list_page(list_page)
        return item_list

    def parse_table(self, zoom):
        my_table = zoom.xpath("./table")[0]
        trs = my_table.xpath("./tbody/tr")
        table = []
        for tr in trs:
            tr_line = []
            tds = tr.xpath("./td")
            for td in tds:
                tr_line.append(td.text_content())
            table.append(tr_line)
        return "\r\n" + "{}".format(table)

    def parse_detail_page(self, detail_page):
        doc = html.fromstring(detail_page)
        zoom = doc.xpath("//div[@id='zoom']")[0]
        try:
            table = self.parse_table(zoom)
        except:
            table = []
        if table:
            contents = []
            for node in zoom:
                if node.tag == "table":
                    pass
                    # 表格不需要 也不需要替换 pdf
                    # contents.append(self.parse_table(zoom))
                else:
                    contents.append(node.text_content())
            return "".join(contents)

        else:
            detail_content = zoom.text_content()
            return detail_content

    def parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        news_area = doc.xpath("//div[@opentype='page']")[0]
        news_title_parts = news_area.xpath("//font[@class='newslist_style']")
        items = []

        for news_title_part in news_title_parts:
            item = {}
            # TODO 应对 105, 109, 112 等不太符合规范的列表页
            try:
                news_date_part = news_title_part.xpath("./following-sibling::span[@class='hui12']")[0].text_content()
            except:
                news_date_part = news_title_part.xpath("./following-sibling::a/span[@class='hui12']")[0].text_content()
            # print(news_date_part)
            item["pubdate"] = news_date_part   # 发布时间

            news_title = news_title_part.xpath("./a")[0].text_content()
            # print(news_title)
            item["article_title"] = news_title  # 文章标题

            news_link = news_title_part.xpath("./a/@href")[0]
            news_link = "http://www.pbc.gov.cn" + news_link
            item["article_link"] = news_link  # 文章详情页链接
            # print(news_link)
            items.append(item)

        return items

    def close(self):
        logger.info("爬虫关闭 ")
        self.sql_client.dispose()

    def start(self):
        for page in range(1, 3):

            try:
                items = self.crawl_list(page)
            except:
                items = []
                self.error_pages.append(page)

            for item in items:
                try:
                    detail_page = self.get_page(item["article_link"])
                    item['article_content'] = self.parse_detail_page(detail_page)
                    print(item)
                except:
                    self.error_list.append(item)

        self.close()


if __name__ == "__main__":
    d = ChinaBank()
    d.start()
    print(d.error_list)
    print(d.error_pages)
