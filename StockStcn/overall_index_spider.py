from lxml import html

from StockStcn.base_stcn import STCNBase


class OverAllIndexSpider(STCNBase):

    def __init__(self):
        super(OverAllIndexSpider, self).__init__()
        self.index_url = 'https://www.stcn.com/'

    def start(self):

        index_page = self.get(self.index_url)

        # print(index_page)

        # 找到全部的 a 标签
        doc = html.fromstring(index_page)
        links = doc.xpath(".//a")
        # print(len(links))
        links = [link.xpath("./@href") for link in links]
        links = [link[0] for link in links if (link and isinstance(link, list))]
        # print(links)
        # print(len(links))


if __name__ == "__main__":
    OverAllIndexSpider().start()
