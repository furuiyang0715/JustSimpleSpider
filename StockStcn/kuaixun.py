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


if __name__ == "__main__":
    # STCNKuaixun().start()

    STCNYaoWen().start()

