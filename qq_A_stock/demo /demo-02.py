import json
import pprint

import requests as re
# url = 'https://new.qq.com/ch2/Agu'
# text = re.get(url).text
# print("优质" in text)
# print("孙晨宇" in text)

# durl = "https://pacaio.match.qq.com/irs/rcd?cid=52&token=8f6b50e1667f130c10f981309e1d8200" \
#        "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&page=0&isForce=1&expIds=&callback=__jp1"

durl = "https://pacaio.match.qq.com/irs/rcd?cid=52&token=8f6b50e1667f130c10f981309e1d8200" \
       "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&callback=__jp1"

# 未登录
# durl = "https://pacaio.match.qq.com/irs/rcd?cid=52&token=8f6b50e1667f130c10f981309e1d8200" \
#        "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&page=0&isForce=1&expIds=&callback=__jp0"


# durl = "https://pacaio.match.qq.com/irs/rcd?cid=92&token=54424c1ebe77ea829a41040a3620d0e7" \
#        "&ext=finance_stock&page=0&expIds=&callback=__jp2"

# 3911,3922,3923,3914,3913,3930,3915,3918,3908 代表了一个 A 股的新分类么 ？？

# 生成 token
# 测试生成 token
ret = re.get(durl).text
print(ret)   # "msg":"auth error"
print(type(ret))
ret = ret.lstrip("__jp1(")
ret = ret.rstrip(")")
ret = json.loads(ret)
# print(pprint.pformat(ret))
# print(ret.keys())
# dict_keys(['code', 'msg', 'data', 'datanum', 'seq', 'biz', 's_group', 'other'])
# print(ret.get('code'))  # 0
# print(ret.get('msg'))  # ''
# print(ret.get('data'))  # []
# print(ret.get("datanum"))  # 20
# print(ret.get("seq"))  # 20200210094908-wtnzZpfiCdEy8lFb
# print(ret.get("biz"))  # 5000
# print(ret.get("s_group"))  # None

data = ret.get("data")
# print(data)
# t1 = data[0]
# print(pprint.pformat(t1))

# 拿到全部的文章 （不要专题）
# articles = [d.get("title") for d in data if d.get("article_type") == 0]
# print(pprint.pformat(articles))
# pub_dates = [d.get("publish_time") for d in data if d.get("article_type") == 0]
# print(pprint.pformat(pub_dates))   # 发布时间是无序的
# update_dates = [d.get("update_time") for d in data if d.get("article_type") == 0]
# print(pprint.pformat(update_dates))   # 更新时间也是无序的

# t2 = data[-1]
# print(pprint.pformat(t2))
