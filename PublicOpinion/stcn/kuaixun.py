import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_Kuaixun(STCN_Base):
    # 快讯
    def __init__(self):
        super(STCN_Kuaixun, self).__init__()
        self.format_url = "http://kuaixun.stcn.com/index_{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '快讯'

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = utils.parse_list_items_2(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    kuaixun = STCN_Kuaixun()
    kuaixun._start()
