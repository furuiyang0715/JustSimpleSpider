from lxml import html

from StockStcn.base_stcn import STCN_Base
from StockStcn import stcn_utils as utils


class STCN_RenWu(STCN_Base):
    # 人物
    def __init__(self):
        super(STCN_RenWu, self).__init__()
        self.format_url = "http://news.stcn.com/renwu/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '人物'


    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    rw = STCN_RenWu()
    rw._start()
