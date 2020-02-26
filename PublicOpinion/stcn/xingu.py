from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_XinGu(STCN_Base):
    # 新股
    def __init__(self):
        super(STCN_XinGu, self).__init__()
        self.format_url = "http://stock.stcn.com/xingu/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '新股'

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = utils.parse_list_items_3(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    dapan = STCN_XinGu()
    dapan._start()
