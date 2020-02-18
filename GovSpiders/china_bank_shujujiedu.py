import time

from lxml import html
from GovSpiders.base_spider import BaseSpider


class ChinaBankShuJuJieDu(BaseSpider):
    def __init__(self):
        super(ChinaBankShuJuJieDu, self).__init__()
        self.name = '中国银行-数据解读'
        self.table = 'chinabank_shujujiedu'
        self.start_url = 'http://www.pbc.gov.cn/diaochatongjisi/116219/116225/11871/index{}.html'

    def _parse_table(self, zoom):
        my_table = zoom.xpath("./table")[0]
        trs = my_table.xpath("./tbody/tr")
        table = []
        for tr in trs:
            tr_line = []
            tds = tr.xpath("./td")
            for td in tds:
                tr_line.append(td.text_content())
            table.append(tr_line)
        return "\r\n" + "{}".format(table)

    def _parse_detail_page(self, detail_page):
        doc = html.fromstring(detail_page)
        zoom = doc.xpath("//div[@id='zoom']")[0]
        try:
            table = self._parse_table(zoom)
        except:
            table = []
        if table:
            contents = []
            for node in zoom:
                if node.tag == "table":
                    pass
                else:
                    contents.append(node.text_content())
            return "".join(contents)

        else:
            detail_content = zoom.text_content()
            return detail_content

    def _parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        news_area = doc.xpath("//div[@opentype='page']")[0]
        news_title_parts = news_area.xpath("//font[@class='newslist_style']")
        items = []
        for news_title_part in news_title_parts:
            item = {}
            try:
                news_date_part = news_title_part.xpath("./following-sibling::span[@class='hui12']")[0].text_content()
            except:
                news_date_part = news_title_part.xpath("./following-sibling::a/span[@class='hui12']")[0].text_content()
            item["pubdate"] = news_date_part
            news_title = news_title_part.xpath("./a")[0].text_content()
            item["article_title"] = news_title
            news_link = news_title_part.xpath("./a/@href")[0]
            news_link = "http://www.pbc.gov.cn" + news_link
            item["article_link"] = news_link
            items.append(item)
        return items

    def process_list(self, page_num):
        list_retry = 2
        try:
            list_page = self.fetch_page(self.start_url.format(page_num))
            if list_page:
                items = self._parse_list_page(list_page)
            else:
                raise
        except:
            list_retry -= 1
            if list_retry < 0:
                return
            self.process_list(page_num)
        else:
            return items

    def process_detail(self, link):
        detail_retry = 2
        try:
            detail_page = self.fetch_page(link)
            if detail_page:
                article = self._parse_detail_page(detail_page)
            else:
                raise
        except:
            detail_retry -= 1
            if detail_retry < 0:
                return
            self.process_detail(link)
        else:
            return article

    def _start(self, page_num):
        items = self.process_list(page_num)
        if items:
            for item in items:
                link = item["article_link"]
                article = self.process_detail(link)
                if article:
                    item['article_content'] = article
                    ret = self.save(item)
                    if not ret:
                        self.error_detail.append(item.get("article_link"))
                else:
                    self.error_detail.append(link)
        else:
            self.error_list.append(self.start_url.format(page_num))


if __name__ == "__main__":
    demo = ChinaBankShuJuJieDu()
    demo._start(1)
    print(demo.error_list)
    print(demo.error_detail)

