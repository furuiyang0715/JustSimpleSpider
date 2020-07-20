import json
import time

# _ts = 1595213398000
# # _ts = 1595213834525
# print(_ts)
# print(time.time())
# ret = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_ts / 1000))
# print(ret)
import requests

format_url = 'https://v2.sohu.com/integration-api/mix/region/94?\
secureScore=50\
&page=%s\
&size=24\
&pvId=1595213834487tTwv6Ur\
&mpId=0\
&adapter=default\
&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI\
&channel=15\
&requestId=2006120915066717__{}'.format(int(time.time() * 1000))

headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'cookie': 'SUV=2006120915066717; gidinf=x099980107ee11ac7185448570007cf53d61c5dff4ba; __gads=ID=9bb1261cd25d5ccb:T=1593754903:S=ALNI_MZtjTDJngTMkxi5M1Wu9GisGWKLMw; t=1594459538752; IPLOC=CN4400; _muid_=1595214233823230; MTV_SRC=10010001',
}


def get_list(list_url):
    resp = requests.get(list_url, headers=headers)
    if resp and resp.status_code == 200:
        body = resp.text
        datas = json.loads(body).get("data")
        datas = [data for data in datas if data['resourceType'] == 1]

        for data in datas:
            print(data.get("mobileTitle"))

    print()
    print()
    print()

url1 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=2&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225254182'
url2 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=3&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225257057'
url3 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=4&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225258808'
url4 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=5&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225570222'
url5 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=14&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&refer=https%3A%2F%2Ftower.im%2F&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225751598'

url_list = [url1,
            url2,
            url3,
            url4,
            url5,
            ]
for _url in url_list:
    get_list(_url)
