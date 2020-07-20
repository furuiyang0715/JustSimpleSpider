import json
import pprint
import sys
import time

import requests

start_ts = int(time.time() * 1000)

format_url = 'https://v2.sohu.com/integration-api/mix/region/94?\
secureScore=50\
&page=1\
&size=24\
&pvId=1595213834487tTwv6Ur\
&mpId=0\
&adapter=default\
&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI\
&channel=15\
&requestId=2006120915066717__{}'

first_url = format_url.format(start_ts)
resp = requests.get(first_url)
items = []
if resp and resp.status_code == 200:
    datas = json.loads(resp.text).get("data")
    _ts = datas[-1].get("publicTime")
    datas = [data for data in datas if data['resourceType'] == 1]
    for data in datas:
        # print(pprint.pformat(data))
        item = dict()
        # https://m.sohu.com/a/408372635_100141583
        item['link'] = "https://m.sohu.com" + data.get("url")
        item['title'] = data.get("mobileTitle")
        item['pub_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get("publicTime") / 1000))
        print(item)
