import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_KanDianShuJu(STCN_Base):
    # 看点数据
    def __init__(self):
        super(STCN_KanDianShuJu, self).__init__()
        self.format_url = "http://data.stcn.com/kandianshuju/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '看点数据'

    def _parse_list_body(self, body):

        # print(body)
        # sys.exit(0)

        doc = html.fromstring(body)
        items = utils.parse_list_items_3(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    kandianshuju = STCN_KanDianShuJu()
    kandianshuju._start()
