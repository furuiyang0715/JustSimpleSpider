import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_Finance(STCN_Base):
    # 机构
    def __init__(self):
        super(STCN_Finance, self).__init__()
        self.list_url = "http://finance.stcn.com/"

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        first = utils.parse_list_first(doc)
        self._add_article(first)
        # print(first)
        # print(body)
        # sys.exit(0)
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        # print(pprint.pformat(items))
        items.append(first)
        return items


if __name__ == "__main__":
    f = STCN_Finance()
    f._start()
