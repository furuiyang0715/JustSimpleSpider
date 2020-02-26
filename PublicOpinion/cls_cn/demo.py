import json
import pprint

url = 'https://www.cls.cn/nodeapi/telegraphs?' \
      'refresh_type=1' \
      '&rn=20' \
      '&last_time=1582704958' \
      '&token=' \
      '&app=CailianpressWeb' \
      '&os=web' \
      '&sv=6.8.0' \
      '&sign=eb54fd54614368f75c0f42c510a607b2'


url = 'https://www.cls.cn/telegraph'

headers = {
# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
# 'Cache-Control': 'no-cache',
# 'Connection': 'keep-alive',
# 'Cookie': 'HWWAFSESID=e140c910fe7046a52d4; HWWAFSESTIME=1582704679228; Hm_lvt_fa5455bb5e9f0f260c32a1d45603ba3e=1582704686; Hm_lpvt_fa5455bb5e9f0f260c32a1d45603ba3e=1582704767',
# 'Cookie': 'HWWAFSESID=e140c910fe7046a52d4; HWWAFSESTIME=1582704679228; Hm_lvt_fa5455bb5e9f0f260c32a1d45603ba3e=1582704686; Hm_lpvt_fa5455bb5e9f0f260c32a1d45603ba3e=1582705543',
# 'Host': 'www.cls.cn',
# 'Pragma': 'no-cache',
# 'Sec-Fetch-Mode': 'navigate',
# 'Sec-Fetch-Site': 'same-origin',
# 'Sec-Fetch-User': '?1',
# 'Upgrade-Insecure-Requests': '1',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

url = 'https://www.cls.cn/nodeapi/telegraphs?refresh_type=1&rn=20&last_time=1582703853&sign=56918b10789cb8a977c518409e7f0ced'


# last_time 是某个条目的发布时间
# 从这个时间开始向前取出 rn 个数据

# 所以逻辑就是先拿出当前的时间, 然后将其转换为时间戳
# 取出最新的 rn 个, 然后去最后一个数据的时间戳 下一次回传进去 继续向离现在更远的时间点推进

# sign 不知道是怎么生成的，貌似是个不变值 。。 TODO

import requests as req

ret = req.get(url, headers=headers).text

py_data = json.loads(ret)

infos = py_data.get("data").get('roll_data')

# print(pprint.pformat(py_data))


# print(type(infos))
# print(len(infos))
# print(pprint.pformat(infos[0]))

one = {'ad': {'adTag': '',
        'fullScreen': 0,
        'id': 0,
        'img': '',
        'monitorUrl': '',
        'title': '',
        'url': '',
        'video_url': ''},
 'audio_url': ['https://image.cailianpress.com/admin/20200226/160037gEet6QonmLwI.mp3'],
 'author_extends': '',
 'bold': 0,
 'brief': '【科技类ETF被监管窗口指导？基金公司表示并未有限制规模等约束性指导】今日市场传闻“科技类ETF被监管窗口指导”，经记者从相关基金公司获悉，他们仅接到监管了解情况的问询，并未有限制规模等约束性指导。（财联社记者 '
          '陈默）',
 'category': '',
 'collection': 0,
 'comment_num': 11,
 'confirmed': 1,
 'content': '【科技类ETF被监管窗口指导？基金公司表示并未有限制规模等约束性要求】财联社2月26日讯，今日市场传闻“科技类ETF被监管窗口指导”，经记者从相关基金公司获悉，他们仅接到监管了解情况的问询，并未有限制规模等约束性指导。（财联社记者 '
            '陈默）',   # 内容
 'ctime': 1582703853,   # new Date(1582703853 * 1000)  发布时间
 'deny_comment': 0,
 'depth_extends': '[]',
 'explain_num': -1,
 'has_img': 0,
 'id': 447808,
 'images': [],
 'img': '',
 'imgs': [],
 'in_roll': 1,
 'is_ad': 0,
 'is_top': 0,
 'jpush': 1,
 'level': 'B',
 'modified_time': 1582704036,
 'reading_num': 201379,
 'recommend': 1,
 'share_img': 'https://image.cailianpress.com/share/roll.png',
 'share_num': 966,
 'shareurl': 'https://api3.cls.cn/share/article/447808?os=&sv=6.9.8&app=CailianpressWap',
 'sort_score': 1582703853,
 'status': 1,
 'stock_list': [],
 'sub_titles': [],
 'subjects': [{'article_id': 447808,
               'attention_num': 0,
               'category_id': 0,
               'is_attention': False,
               'subject_description': '',
               'subject_id': 1349,
               'subject_img': '',
               'subject_name': '公募基金动态'},
              {'article_id': 447808,
               'attention_num': 0,
               'category_id': 0,
               'is_attention': False,
               'subject_description': '',
               'subject_id': 1777,
               'subject_img': '',
               'subject_name': '科创板最新动态'}],
 'tags': [],
 'title': '科技类ETF被监管窗口指导？基金公司表示并未有限制规模等约束性要求',    # 标题
 'type': -1,
 'user_id': 253}



'''
code:  可为空 
link:  可为空
pub_date: 可为空  
title: 不为空 
content: 不为空 
'''