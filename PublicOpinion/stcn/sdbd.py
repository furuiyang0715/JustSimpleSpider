from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_SDBD(STCN_Base):
    # 深度报道
    def __init__(self):
        super(STCN_SDBD, self).__init__()
        self.format_url = "http://news.stcn.com/sdbd/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '深度报道'

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        print(len(items))
        return items


if __name__ == "__main__":
    sd = STCN_SDBD()
    sd._start()
