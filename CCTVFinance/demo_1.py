import json
import pprint
import re

import requests

url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/economy_1.jsonp?cb=economy'
resp = requests.get(url)
if resp.status_code == 200:
    body = resp.text.encode("ISO-8859-1").decode("utf-8")
    # print(body)
    datas_str = re.findall("economy\((.*)\)", body)[0]
    # print(datas_str)
    datas = json.loads(datas_str).get("data").get("list")
    # print(pprint.pformat(datas))
    print(len(datas))

    # for data in datas:
    #     print(data)
