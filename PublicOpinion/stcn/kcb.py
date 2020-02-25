import sys

from lxml import html

from PublicOpinion.stcn import stcn_utils as utils
from PublicOpinion.stcn.base_stcn import STCN_Base


class STCN_KCB(STCN_Base):
    # 科创板
    def __init__(self):
        super(STCN_KCB, self).__init__()
        self.list_url = "http://kcb.stcn.com/news/index.shtml"

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = utils.parse_list_items(doc)
        [self._add_article(item) for item in items]
        print(len(items))
        return items


if __name__ == "__main__":
    d = STCN_KCB()
    d._start()
