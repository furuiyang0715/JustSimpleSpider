from lxml import html
from Takungpao.base import TakungpaoBase
from base import logger


class HKStock_CJSS(TakungpaoBase):
    def __init__(self):
        super(HKStock_CJSS, self).__init__()
        self.page = 3
        self.name = '财经时事'
        self.first_url = 'http://finance.takungpao.com/hkstock/cjss/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/cjss/index_{}.html"

    def _parse_detail(self, body):
        result = self.extractor.extract(body)
        content = result.get("content")
        return content

    def parse_list(self, body):
        items = []
        doc = html.fromstring(body)
        news_list = doc.xpath("//div[@class='m_txt_news']/ul/li")
        # print(news_list)
        # print(len(news_list))
        for news in news_list:
            item = {}
            title = news.xpath("./a[@class='a_title']")
            if not title:
                title = news.xpath("./a[@class='a_title txt_blod']")
            title = title[0].text_content()
            # print(title)
            item['title'] = title
            pub_date = news.xpath("./a[@class='a_time txt_blod']")
            if not pub_date:
                pub_date = news.xpath("./a[@class='a_time']")

            link = pub_date[0].xpath("./@href")[0]
            # print(link)
            item['link'] = link

            pub_date = pub_date[0].text_content()
            # print(pub_date)
            item['pub_date'] = pub_date
            items.append(item)

            detail_resp = self.get(link)
            if detail_resp and detail_resp.status_code == 200:
                article = self._parse_detail(detail_resp.text)
                if article:
                    article = self._process_content(article)
                    item['article'] = article
                    print(item)
        return items

    def start(self):
        self._create_table()
        self._spider_init()
        for page in range(1, self.page+1):
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)

            list_resp = self.get(list_url)
            if list_resp and list_resp.status_code == 200:
                items = self.parse_list(list_resp.text)
                page_save_num = self._batch_save(self.spider_client, items, self.table_name, self.fields)
                logger.info(f"第{page}页保存成功的个数{page_save_num}")


class HKStock_QQGS(HKStock_CJSS):
    def __init__(self):
        super(HKStock_QQGS, self).__init__()
        self.page = 3
        self.name = '全球股市'
        self.first_url = 'http://finance.takungpao.com/hkstock/qqgs/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/qqgs/index_{}.html"


if __name__ == "__main__":
    # cjss = HKStock_CJSS()
    # cjss.start()

    qqgs = HKStock_QQGS()
    qqgs.start()
