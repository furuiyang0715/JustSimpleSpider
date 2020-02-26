import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class ZXDT_YQJJ(STCN_Base):
    # 中心动态
    def __init__(self):
        super(ZXDT_YQJJ, self).__init__()
        self.format_url = "http://yq.stcn.com/zxdt/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 4
        self.name = '中心动态'

    def _parse_list_body(self, body):
        # print(body)
        # sys.exit(0)
        doc = html.fromstring(body)
        items = utils.parse_list_items_5(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    zx = ZXDT_YQJJ()
    zx._start()
