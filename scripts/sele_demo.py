headers = {
    # ":authority": 'docs.qq.com',
    # ":method": 'GET',
    # ":path": '/dop-api/opendoc?normal=1&id=DZXNSSnJudmRtclpr',
    # ":scheme": 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'cookie': 'tvfe_boss_uuid=533c08d6fe58e718; pgv_pvid=4494151490; pgv_pvi=9288806400; RK=da7Ag9pC/h; ptcz=63b49b79fa30c4f3f8580143b0baba6f0f0f7e778b9e956a0a34c884f28a2cd6; o_cookie=2564493603; ied_qq=o2564493603; xw_main_login=qq; XWINDEXGREY=0; pac_uid=1_2564493603; hashkey=24bebbed; TOK=805edda60fea86be; pgv_si=s3244666880; uin=o2564493603; skey=@ZdbV8ES3S; p_uin=o2564493603; pt4_token=*S1-nikhBvaueBnDBYBJOEw2s*aC22*s9wRpVbEMKQ4_; p_skey=V-ZtxHv50f-kRVRVrlKgveFyBpf2eakg2eqpvlDiLx8_; p_luin=o2564493603; p_lskey=0004000074b426ec755c90ce174e46e8379fa3632e9763d8d23bab617e1f541277f4273faa652e0ee96b4b54; has_been_login=1; uid=144115210459136146; uid_key=da6nrMTMhC%2FMkDb9Dl8cgXSk4T3IKT%2F7Z7DAkbwVbCXYs%2Fp3FCNy5dTbfuGGfCEJZ0OZ3TmRGKjxPe3nn998wMqR9Y9PkuIF; utype=qq; vfwebqq=0aa6d92ddcb822389418f46905c0f9a34a6ad4a23f4250d4be4475491c0cc542128509c57d9e7c86; loginTime=1587097149209; ES2=b6f705489caf6413',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}

import requests as re
import json
import pprint

# https://docs.qq.com/doc/DZGNueENmTklhdHFo
# url = 'https://docs.qq.com/dop-api/opendoc?normal=1&id=DZXNSSnJudmRtclpr'
url = 'https://docs.qq.com/dop-api/opendoc?normal=1&id=DZGNueENmTklhdHFo'

text = re.get(url, headers=headers).text
_start = text.find("{")
text = text[_start:]
print(pprint.pformat(text))
data = json.loads(text)
print(data.get("clientVars").get("padTitle"))


# from selenium import webdriver
# import time
#
# browser = webdriver.Chrome()
# browser.get(url)
# time.sleep(10)
# page = browser.page_source
# print(page)  # selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 79
# browser.close()

# from selenium import webdriver
# options = webdriver.ChromeOptions()
# # options.add_argument('lang=zh_CN.UTF-8')
# options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
# browser = webdriver.Chrome(chrome_options=options)
# browser.get(url)
# print(browser.page_source)
# browser.quit()
