from lxml import html

from StockStcn.base_stcn import STCN_Base
from StockStcn import stcn_utils as utils


class STCN_SBDT(STCN_Base):
    # 时报动态
    def __init__(self):
        super(STCN_SBDT, self).__init__()
        self.format_url = "http://news.stcn.com/sbdt/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 4
        self.name = '时报动态'

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    sb = STCN_SBDT()
    sb._start()
