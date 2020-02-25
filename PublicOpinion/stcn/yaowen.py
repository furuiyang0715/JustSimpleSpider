import sys

from lxml import html

from PublicOpinion.stcn import stcn_utils as utils
from PublicOpinion.stcn.base_stcn import STCN_Base


class STCN_YaoWen(STCN_Base):
    def __init__(self):
        super(STCN_YaoWen, self).__init__()
        self.list_url = "http://news.stcn.com/"

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        first = utils.parse_list_first(doc)
        self._add_article(first)

        columns = utils.parse_list_items_1(doc)
        [self._add_article(column) for column in columns]
        columns.append(first)

        return columns


if __name__ == "__main__":
    yaowen = STCN_YaoWen()
    yaowen._start()