from lxml import html
from StockStcn import stcn_utils as utils
from StockStcn.base_stcn import STCNBase


class STCNKuaixun(STCNBase):
    def __init__(self):
        super(STCNKuaixun, self).__init__()
        self.format_url = "http://kuaixun.stcn.com/index_{}.html"
        self.name = '快讯'
        self.base_url = 'http://kuaixun.stcn.com/'

    def _create_table(self):
        pass

    def extract_content(self, body):
        try:
            result = self.extractor.extract(body)
            content = result.get("content")
        except:
            return ''
        else:
            return content

    def parse_detail(self, body):
        try:
            doc = html.fromstring(body)
            node = doc.xpath("//div[@class='txt_con']")[0]
            content = node.text_content()
        except:
            content = None
        else:
            return content
        if not content:
            content = self.extract_content(body)
            return content

    def add_article(self, item: dict):
        link = item.get("link")
        if link:
            link = self.base_url + item['link'][2:]
            item['link'] = link
            detail_page = self.get(link)
            if detail_page:
                article = self.parse_detail(detail_page)
                if article:
                    item['article'] = article
                    return True
        return False

    def parse_list_body(self, body):
        try:
            doc = html.fromstring(body)
            items = utils.parse_list_items_2(doc)
            # 根据某个条件进行过滤
            [self.add_article(item) for item in items]
            return items
        except:
            return []

    def start(self):
        self._create_table()
        for page in range(1, 3):
            list_url = self.format_url.format(page)
            list_page = self.get(list_url)
            if list_page:
                items = self.parse_list_body(list_page)
                for item in items:
                    print(item)


if __name__ == "__main__":
    kuaixun = STCNKuaixun()
    kuaixun.start()
