from gne import GeneralNewsExtractor
from lxml import html

from PublicOpinion.takungpao.hkstock_cjss import Base


class Travel(Base):
    def __init__(self):
        super(Travel, self).__init__()
        self.first_url = 'http://finance.takungpao.com/travel/index.html'
        self.format_url = 'http://finance.takungpao.com/travel/index_{}.html'
        self.name = '旅游'
        self.table = 'takungpao'
        self.fields = ['link', 'title', 'pub_date', 'article']
        self.extractor = GeneralNewsExtractor()
        self.page = 19

    def _parse_detail(self, body):
        try:
            result = self.extractor.extract(body)
            content = result.get("content")
            return content
        except:
            print("解析详情页失败 ..")
            return None

    def _parse_list(self, body):
        doc = html.fromstring(body)
        news_list = doc.xpath('//div[@class="txtImgListeach current"]')
        print(len(news_list))

        items = []
        for news in news_list:
            item = {}
            link = news.xpath("./h3/a/@href")[0]
            # print(link)
            item['link'] = link
            title = news.xpath("./h3/a")[0].text_content()
            # print(title)
            item['title'] = title
            pub_date = news.xpath(".//span[@class='time']")[0].text_content()
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
        return items

    def _start(self):
        for page in range(1, self.page+1):
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)
            list_resp = self.get(list_url)
            if list_resp:
                list_page = list_resp.text
                items = self._parse_list(list_page)
                self.save(items)


if __name__ == "__main__":
    t = Travel()
    t.start()
