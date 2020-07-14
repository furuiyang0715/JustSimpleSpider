import datetime

from lxml import html
from StockStcn import stcn_utils as utils
from StockStcn.base_stcn import STCNBase
from base import logger


class STCNKuaixun(STCNBase):
    def __init__(self):
        super(STCNKuaixun, self).__init__()
        self.base_url = 'http://kuaixun.stcn.com/'
        self.first_url = 'http://kuaixun.stcn.com/index.html'
        self.format_url = "http://kuaixun.stcn.com/index_{}.html"
        self.name = '快讯'
        self.list_parse_func = utils.parse_list_items_2


class STCNYaoWen(STCNBase):
    def __init__(self):
        super(STCNYaoWen, self).__init__()
        self.base_url = "http://news.stcn.com/"
        self.first_url = 'https://news.stcn.com/news/index.html'       # 第 1 页
        self.format_url = 'https://news.stcn.com/news/index_{}.html'   # 从 1 开始是第 2 页
        self.name = '要闻'
        self.list_parse_func = utils.parse_list_items_1

    def parse_list_body(self, body):
        doc = html.fromstring(body)
        first = utils.parse_list_first(doc)
        logger.info(first)
        columns = self.list_parse_func(doc)
        columns = [column for column in columns if self.add_article(column)]
        if self.add_article(first):
            columns.append(first)
        return columns


class STCNCompany(STCNBase):
    def __init__(self):
        super(STCNCompany, self).__init__()
        self.base_url = "http://company.stcn.com/"
        self.first_url = 'https://company.stcn.com/index.html'
        self.format_url = 'https://company.stcn.com/index_{}.html'
        self.name = '公司'
        self.list_parse_func = utils.parse_list_items_1

    def parse_list_body(self, body):
        doc = html.fromstring(body)
        first = utils.parse_list_first(doc)
        logger.info(first)
        columns = self.list_parse_func(doc)
        columns = [column for column in columns if self.add_article(column)]
        if self.add_article(first):
            columns.append(first)
        return columns


class STCNColumn(STCNBase):
    def __init__(self):
        super(STCNColumn, self).__init__()
        self.base_url = "http://space.stcn.com/tg"
        self.first_url = 'http://space.stcn.com/tg/index.html'
        self.format_url = 'http://space.stcn.com/tg/index_{}.html'
        self.name = '专栏'

    def parse_list_body(self, body):
        doc = html.fromstring(body)
        items = []
        columns = doc.xpath('//div[@id="news_list2"]/dl')
        for column in columns:
            print(column)
            title = column.xpath('./dd[@class="mtit"]/a/@title')[0]
            link = column.xpath('./dd[@class="mtit"]/a/@href')[0]
            pub_date = column.xpath('./dd[@class="mexp"]/span')[0].text_content()
            my_today = datetime.datetime.today()
            yesterday = datetime.datetime.today()-datetime.timedelta(days=1)
            before_yesterday = datetime.datetime.today()-datetime.timedelta(days=2)
            pub_date = pub_date.replace("今天", my_today.strftime("%Y-%m-%d"))
            pub_date = pub_date.replace("昨天", yesterday.strftime("%Y-%m-%d"))
            pub_date = pub_date.replace("前天", before_yesterday.strftime("%Y-%m-%d"))

            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self.get(link)
            if detail_body:
                article = self.parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    print(item)
                    items.append(item)
        return items


if __name__ == "__main__":
    # STCNKuaixun().start()

    # STCNYaoWen().start()

    # STCNCompany().start()

    STCNColumn().start()

