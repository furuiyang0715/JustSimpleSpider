from lxml import html
from retrying import retry

from GovSpiders.base_spider import GovBaseSpider


class ChinaBankMixin(object):
    """适用于中国银行的数据解析混入类"""
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

    def parse_detail_page(self, detail_page):
        try:
            article = self._parse_detail_page(detail_page)
        except:
            return None
        else:
            return article

    @retry(stop_max_attempt_number=10)
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
            item["pub_date"] = news_date_part
            news_title = news_title_part.xpath("./a")[0].text_content()
            item["title"] = news_title
            news_link = news_title_part.xpath("./a/@href")[0]
            news_link = "http://www.pbc.gov.cn" + news_link
            item["link"] = news_link
            items.append(item)
        return items

    def parse_list_page(self, list_page):
        try:
            items = self._parse_list_page(list_page)
        except:
            return []
        else:
            return items


class ChinaBankShuJuJieDu(GovBaseSpider, ChinaBankMixin):
    def __init__(self):
        super(ChinaBankShuJuJieDu, self).__init__()
        self.name = '中国银行-数据解读'
        self.table_name = 'chinabank'
        self.start_url = 'http://www.pbc.gov.cn/diaochatongjisi/116219/116225/11871/index{}.html'
        self.fields = ['pub_date', 'title', 'link', 'article']

    def _create_table(self):
        self._spider_init()
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB AUTO_INCREMENT=15688 DEFAULT CHARSET=utf8mb4 COMMENT='中国银行'; 
        '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def start(self):
        self._create_table()
        for page in range(1, 3):
            ditems = []
            list_url = self.start_url.format(page)
            list_page = self.fetch_page(list_url)
            if list_page:
                items = self.parse_list_page(list_page)
                for item in items:
                    # print(item)
                    detail_page = self.fetch_page(item['link'])
                    if detail_page:
                        article = self.parse_detail_page(detail_page)
                        if article:
                            item['article'] = article
                            print(item)
                            ditems.append(item)
            print("爬取数量: ", len(ditems))
            self._spider_init()
            ret = self._batch_save(self.spider_client, ditems, self.table_name, self.fields)
            print("入库数量: ", ret)


class ChinaBankXinWenFaBu(ChinaBankShuJuJieDu):
    def __init__(self):
        super(ChinaBankXinWenFaBu, self).__init__()
        self.name = '中国银行-新闻发布'
        self.table_name = "chinabank"
        self.start_url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index{}.html"


if __name__ == "__main__":
    # ChinaBankShuJuJieDu().start()

    ChinaBankXinWenFaBu().start()

    pass
