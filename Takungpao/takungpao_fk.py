from gne import GeneralNewsExtractor
from lxml import html

from takungpao import Base


class FK(Base):
    def __init__(self):
        super(FK, self).__init__()
        self.list_url = 'http://finance.takungpao.com/fk/'
        self.extractor = GeneralNewsExtractor()
        self.table = 'Takungpao'
        self.name = '风口'
        self.fields = ['link', 'title', 'pub_date', 'article']

    def _parse_detail(self, body):
        result = self.extractor.extract(body)
        content = result.get("content")
        return content

    def _start(self):
        resp = self.get(self.list_url)
        if resp:
            body = resp.text
            doc = html.fromstring(body)
            news_list = doc.xpath('//div[@class="wrap-l js-list fl_dib"]/ul/li/div[@class="list-text fr_dib"]')
            # print(len(news_list))
            items = []
            for news in news_list:
                item = {}
                # print(news.text_content().split("\r\n"))
                title = news.xpath('./h1/a')[0].text_content()
                # print(title)
                item['title'] = title
                link = news.xpath('./h1/a/@href')[0]
                # print(link)
                item['link'] = link
                pub_date = news.xpath('./div[@class="date"]')[0].text_content()
                # print(pub_date)
                item['pub_date'] = pub_date

                detail_resp = self.get(link)
                if detail_resp:
                    detail_page = detail_resp.text
                    article = self._parse_detail(detail_page)
                    if article:
                        item['article'] = article
                        print(item)
                        items.append(item)
            self.save(items)


if __name__ == "__main__":
    fk = FK()
    fk.start()

