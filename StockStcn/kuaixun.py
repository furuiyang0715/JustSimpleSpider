from lxml import html
from StockStcn import stcn_utils as utils
from StockStcn.base_stcn import STCNBase


class STCNKuaixun(STCNBase):
    def __init__(self):
        super(STCNKuaixun, self).__init__()
        self.format_url = "http://kuaixun.stcn.com/index_{}.html"
        self.name = '快讯'
        self.base_url = 'http://kuaixun.stcn.com/'
        self.fields = ['pub_date', 'code', 'title', 'link', 'article']

    def _create_table(self):
        self._spider_init()
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `code` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '股票代码',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='证券时报'; 
        '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

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
            # 根据是否能获取详情页的条件进行过滤
            items = [item for item in items if self.add_article(item)]
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
                print("爬取数量: ", len(items))
                self._spider_init()
                ret = self._batch_save(self.spider_client, items, self.table_name, self.fields)
                print("入库数量: ", ret)


if __name__ == "__main__":
    kuaixun = STCNKuaixun()
    kuaixun.start()
