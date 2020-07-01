import re

import requests as req

url = 'https://www.guokr.com/ask/highlight/?page=1'

resp = req.get(url)

body = resp.text

# print(body)

# 正则匹配出标题以及链接
# <h2><a target="_blank" href="http://www.guokr.com/question/669761/">印度人把男人的生殖器叫林伽，把女人的生殖器叫瑜尼，林伽和瑜尼的交合，便是瑜伽。这是真还是假的</a></h2>
# <h2><a target="_blank" href="{.?}">{.?}</a></h2>
ret = re.findall('<h2><a target="_blank" href="(.*?)">(.*?)</a></h2>', body)

for one in ret:
    print(one[0], one[1])
