from urllib.parse import urlparse

from lxml import html

from StockStcn.base_stcn import STCNBase


class OverAllIndexSpider(STCNBase):

    def __init__(self):
        super(OverAllIndexSpider, self).__init__()
        self.index_url = 'https://www.stcn.com/'

    def extract_page_links(self, page: str):
        doc = html.fromstring(page)
        links = doc.xpath(".//a")
        links = [link.xpath("./@href") for link in links]
        links = [link[0] for link in links if (link and isinstance(link, list))]
        links = [link for link in links if self.clean_link(link)]
        return links

    def clean_link(self, link: str):
        if not link.startswith("http"):
            return False
        for word in ("pdf", "PDF", "video"):
            if word in link:
                return False
        return True

    def start(self):
        index_page = self.get(self.index_url)
        links = self.extract_page_links(index_page)
        for link in links:
            print(link)
            print(urlparse(link))
            print()


if __name__ == "__main__":
    OverAllIndexSpider().start()
