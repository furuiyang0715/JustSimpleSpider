from lxml import html
from Takungpao.base import TakungpaoBase
from base import logger


class EconomicObserver(TakungpaoBase):
    def __init__(self):
        super(EconomicObserver, self).__init__()
        self.name = '经济观察家'
        self.first_url = 'http://www.takungpao.com/finance/236134/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236134/{}.html'
        self.page = 2

    def _parse_detail(self, link):
        detail_resp = self.get(link)
        if detail_resp and detail_resp.status_code == 200:
            body = detail_resp.text
            result = self.extractor.extract(body)
            content = result.get("content")
            return content

    def _parse_list(self, list_url):
        items = []
        list_resp = self.get(list_url)
        if list_resp and list_resp.status_code == 200:
            list_page = list_resp.text
            doc = html.fromstring(list_page)
            news_list = doc.xpath('//div[@class="sublist_mobile"]/dl[@class="item"]')
            for news in news_list:
                item = {}
                link = news.xpath('./dd[@class="intro"]/a/@href')[0]
                # print(link)
                item['link'] = link

                title = news.xpath("./dd/a/@title")[0]
                # print(title)
                title = self._process_content(title)
                item['title'] = title

                pub_date = news.xpath("./dd[@class='date']/text()")[0]
                pub_date = self._process_pub_dt(pub_date)
                # print(pub_date)
                item['pub_date'] = pub_date

                article = self._parse_detail(link)
                if article:
                    article = self._process_content(article)
                    item['article'] = article
                    # print(item)
                    items.append(item)
        return items

    def start(self):
        self._create_table()
        self._spider_init()
        for page in range(1, self.page + 1):
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)
            items = self._parse_list(list_url)
            page_save_num = self._batch_save(self.spider_client, items, self.table_name, self.fields)
            logger.info("第{}页保存的个数是{}".format(page, page_save_num))
