# from lxml import html
#
# from StockStcn.base_stcn import STCN_Base
# from StockStcn import stcn_utils as utils
#
#
# class STCN_BanKuai(STCN_Base):
#     # 版块
#     def __init__(self):
#         super(STCN_BanKuai, self).__init__()
#         self.format_url = "http://stock.stcn.com/bankuai/{}.shtml"
#         self.pages = True  # 是否需要翻页
#         self.page_num = 21
#         self.name = '版块'
#
#     def _parse_list_body(self, body):
#         '''
#  <ul class="news_list2" id="news_list2">
#     <li >
#         <a href="http://stock.stcn.com/2020/0228/15689653.shtml" target="_blank" title="口罩防护概念逆市大涨,国内复工叠加海外疫情升温,口罩需求仍巨大">口罩防护概念逆市大涨,国内复工叠加海外疫情升温,口罩需求仍巨大</a><span>2020-02-28<i>09:56</i></span>
#     </li>
#         '''
#         # print(body)
#         # sys.exit(0)
#
#         doc = html.fromstring(body)
#         items = utils.parse_list_items_3(doc)
#         [self._add_article(item) for item in items]
#         # print(len(items))
#         return items
#
#
# if __name__ == "__main__":
#     bankuai = STCN_BanKuai()
#     bankuai._start()
