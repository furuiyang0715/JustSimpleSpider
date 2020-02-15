import sys
import time
import traceback

from lxml import html

# from chinabank.base_spider import BaseSpider
# from chinabank.common.sqltools.mysql_pool import MqlPipeline
# from chinabank.my_log import logger
from GovSpiders.base_spider import BaseSpider


class ChinaBankShuJuJieDu(BaseSpider):
    def __init__(self):
        super(ChinaBankShuJuJieDu, self).__init__()
        self.name = '中国银行-数据解读'
        self.table = 'chinabank_shujujiedu'
        self.start_url = 'http://www.pbc.gov.cn/diaochatongjisi/116219/116225/11871/index{}.html'

    def parse_table(self, zoom):
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

    def parse_detail_page(self, detail_page):
        ret = ''
        retry = 2
        while True:
            try:
                ret = self._parse_detail_page(detail_page)
            except:
                retry -= 1
                if retry < 0:
                    break
                time.sleep(3)
            else:
                break
        return ret

    def _parse_detail_page(self, detail_page):
        doc = html.fromstring(detail_page)
        zoom = doc.xpath("//div[@id='zoom']")[0]
        try:
            table = self.parse_table(zoom)
        except:
            table = []
        if table:
            contents = []
            for node in zoom:
                if node.tag == "table":
                    pass
                    # 表格不需要 也不需要替换 pdf
                    # contents.append(self.parse_table(zoom))
                else:
                    contents.append(node.text_content())
            return "".join(contents)

        else:
            detail_content = zoom.text_content()
            return detail_content

    def parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        news_area = doc.xpath("//div[@opentype='page']")[0]
        news_title_parts = news_area.xpath("//font[@class='newslist_style']")
        items = []

        for news_title_part in news_title_parts:
            item = {}
            # TODO 应对 105, 109, 112 等不太符合规范的列表页
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
            yield item
        #     items.append(item)
        # return items

    def _start(self):

        list_page = self.fetch_page(self.start_url.format(1))
        # print(list_page)
        if list_page:
            items = self.parse_list_page(list_page)
            for item in items:
                pass

        sys.exit(0)




        # for page in range(1, 2):
        #     retry = 3
        #     while True:
        #         try:
        #             items = self.crawl_list(page)
        #             for item in items:
        #                 detail_page = self.get_page(item["article_link"])
        #                 item['article_content'] = self.parse_detail_page(detail_page)
        #                 logger.info(item)
        #                 self.save_to_mysql(item)
        #         except Exception:
        #             time.sleep(3)
        #             traceback.print_exc()
        #             retry -= 1
        #             if retry < 0:
        #                 self.error_list.append(page)
        #                 break
        #         else:
        #             logger.info("本页保存成功 {}".format(page))
        #             break


if __name__ == "__main__":
    demo = ChinaBankShuJuJieDu()
    demo._start()
