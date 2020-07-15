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


class STCNEgs(STCNBase):
    def __init__(self):
        super(STCNEgs, self).__init__()
        self.base_url = 'https://kuaixun.stcn.com/egs/'
        self.first_url = 'https://kuaixun.stcn.com/egs/index.html'
        self.format_url = 'https://kuaixun.stcn.com/egs/index_{}.html'
        self.name = 'e公司'
        self.list_parse_func = self.parse_list_items

    @staticmethod
    def parse_list_items(doc):
        items = []
        columns = doc.xpath("//ul[@id='news_list2']/li")
        for column in columns:
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content().strip()[:10]
            pub_time = column.xpath(".//i")[0].text_content()
            pub_date = '{} {}'.format(pub_date, pub_time)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            items.append(item)
        return items


class STCNYanBao(STCNBase):
    def __init__(self):
        super(STCNYanBao, self).__init__()
        self.base_url = 'https://kuaixun.stcn.com/yb/'
        self.first_url = 'https://kuaixun.stcn.com/yb/index.html'
        self.format_url = "https://kuaixun.stcn.com/yb/index_{}.html"
        self.name = '研报'
        self.list_parse_func = utils.parse_list_items_3


class STCNSS(STCNBase):
    def __init__(self):
        super(STCNSS, self).__init__()
        self.base_url = 'https://kuaixun.stcn.com/ss/'
        self.first_url = 'https://kuaixun.stcn.com/ss/index.html'
        self.format_url = 'https://kuaixun.stcn.com/ss/index_{}.html'
        self.name = '时事'
        self.list_parse_func = self.parse_list_items

    @staticmethod
    def parse_list_items(doc):
        '''
<li>
        <a href="./202007/t20200715_2135227.html" class="a1"></a>
        <a href="./202007/t20200715_2135227.html" title="美国政府同意撤销留学生签证新规" target="_blank">美国政府同意撤销留学生签证新规</a>
        <span>
        2020-07-15
        <i>09:26</i>
        </span>
</li>
        '''
        items = []
        columns = doc.xpath("//ul[@id='news_list2']/li")
        for column in columns:
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content().strip()[:10]
            pub_time = column.xpath(".//i")[0].text_content()
            pub_date = '{} {}'.format(pub_date, pub_time)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            items.append(item)
        return items


class CJCNSS(STCNBase):
    def __init__(self):
        super(CJCNSS, self).__init__()
        self.base_url = 'https://kuaixun.stcn.com/cj/'
        self.first_url = 'https://kuaixun.stcn.com/cj/index.html'
        self.format_url = 'https://kuaixun.stcn.com/cj/index_{}.html'
        self.name = '财经'
        self.list_parse_func = self.parse_list_items

    @staticmethod
    def parse_list_items(doc):
        items = []
        columns = doc.xpath("//ul[@id='news_list2']/li")
        for column in columns:
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content().strip()[:10]
            pub_time = column.xpath(".//i")[0].text_content()
            pub_date = '{} {}'.format(pub_date, pub_time)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            items.append(item)
        return items


if __name__ == "__main__":
    # STCNEgs().start()

    # STCNYanBao().start()

    # STCNSS().start()

    # CJCNSS().start()

    pass


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
        columns = doc.xpath('//div[@id="news_list2"]/dl[@class="wapdl"]')
        for column in columns:
            '''
<dl class="wapdl">
    <dt><img src="https://space.stcn.com/tg/202007/W020200713322340541875.png"></dt>
    <dd class="tit"><a href="https://space.stcn.com/tg/202007/t20200713_2126950.html">球鞋垂直电商兴起折射我国消费升级趋势</a></dd>
    <dd class="exp">盘和林<span>07-13 08:57</span></dd>
</dl>
            '''
            title = column.xpath('./dd[@class="tit"]/a')[0].text_content()
            link = column.xpath('./dd[@class="tit"]/a/@href')[0]
            pub_date = column.xpath('./dd[@class="exp"]/span')[0].text_content()
            pub_date = self._process_pub_dt(pub_date)

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
    # STCNColumn().start()
    pass


class STCNMarket(STCNBase):
    def __init__(self):
        super(STCNMarket, self).__init__()
        self.base_url = "http://stock.stcn.com/"
        self.first_url = 'http://stock.stcn.com/index.html'
        self.format_url = 'http://stock.stcn.com/index_{}.html'
        self.name = '股市'
        self.list_parse_func = utils.parse_list_items_1


if __name__ == "__main__":
    # STCNMarket().start()
    pass


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


if __name__ == "__main__":
    STCNCompany().start()
    pass


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


class STCNRoll(STCNBase):
    def __init__(self):
        super(STCNRoll, self).__init__()
        self.base_url = None
        self.first_url = 'https://www.stcn.com/gd/index.html'
        self.format_url = "https://www.stcn.com/gd/index_{}.html"
        self.name = '滚动'

    def parse_list_body(self, body):
        items = []
        doc = html.fromstring(body)
        columns = doc.xpath("//ul[@id='news_list2']/li")
        num = 0
        for column in columns:
            num += 1
            title = column.xpath("./a")[-1].xpath("./@title")[0]
            link = column.xpath("./a")[-1].xpath("./@href")[0]
            pub_date = column.xpath("./span")[0].text_content().strip()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[-5:])
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            items.append(item)
        items = [item for item in items if self.add_article(item)]
        return items


class STCNSDBD(STCNBase):
    def __init__(self):
        super(STCNSDBD, self).__init__()
        self.base_url = 'https://news.stcn.com/sd/'
        self.first_url = 'https://news.stcn.com/sd/index.html'
        self.format_url = "https://news.stcn.com/sd/index_{}.html"
        self.name = '深度'
        self.list_parse_func = utils.parse_list_items_1


class STCNXWPL(STCNBase):
    def __init__(self):
        super(STCNXWPL, self).__init__()
        self.base_url = 'https://news.stcn.com/pl/'
        self.first_url = 'https://news.stcn.com/pl/index.html'
        self.format_url = "https://news.stcn.com/pl/index_{}.html"
        self.name = '评论'
        self.list_parse_func = utils.parse_list_items_1


if __name__ == "__main__":

    # STCNYaoWen().start()

    # STCNRoll().start()

    # STCNSDBD().start()

    # STCNXWPL().start()

    pass


class STCNFinance(STCNBase):
    def __init__(self):
        super(STCNFinance, self).__init__()
        self.base_url = None
        self.first_url = 'http://finance.stcn.com/index.html'
        self.format_url = "http://finance.stcn.com/index_{}.html"
        self.name = '机构'
        self.list_parse_func = self.parse_list_items

    @staticmethod
    def parse_list_items(doc):
        '''
            <li>
            <a href="https://news.stcn.com/news/202007/t20200715_2135183.html" class="a1"></a>
            <a href="https://news.stcn.com/news/202007/t20200715_2135183.html" title="可转债新券持续受捧 7月以来打新户数增百万" target="_blank">可转债新券持续受捧 7月以来打新户数增百万</a>
            <span>
            2020-07-15
            <i>09:06</i>
            </span>
            </li>
        '''
        items = []
        columns = doc.xpath("//ul[@id='news_list2']/li")
        for column in columns:
            title = column.xpath("./a/@title")[0]
            link = column.xpath("./a/@href")[0]
            pub_date = column.xpath("./span")[0].text_content().strip()[:10]
            pub_time = column.xpath(".//i")[0].text_content()
            pub_date = '{} {}'.format(pub_date, pub_time)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            items.append(item)
        return items


if __name__ == "__main__":
    # STCNFinance().start()
    pass
