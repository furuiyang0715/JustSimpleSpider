import json
import time

import requests


class SuhuFinance(object):
    def __init__(self):
        self.format_url = 'https://v2.sohu.com/integration-api/mix/region/94?\
secureScore=50\
&page=%s\
&size=24\
&pvId=1595213834487tTwv6Ur\
&mpId=0\
&adapter=default\
&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI\
&channel=15\
&requestId=2006120915066717__{}'.format(int(time.time() * 1000))
        self.headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'cookie': 'SUV=2006120915066717; gidinf=x099980107ee11ac7185448570007cf53d61c5dff4ba; __gads=ID=9bb1261cd25d5ccb:T=1593754903:S=ALNI_MZtjTDJngTMkxi5M1Wu9GisGWKLMw; t=1594459538752; IPLOC=CN4400; _muid_=1595214233823230; MTV_SRC=10010001',
        }

    def get_list_items(self, url):
        resp = requests.get(url, headers=self.headers)
        items = []
        if resp and resp.status_code == 200:
            datas = json.loads(resp.text).get("data")
            _ts = datas[-1].get("publicTime")
            datas = [data for data in datas if data['resourceType'] == 1]
            for data in datas:
                item = dict()
                # https://m.sohu.com/a/408372635_100141583
                item['link'] = "https://m.sohu.com" + data.get("url")
                item['title'] = data.get("mobileTitle")
                item['pub_date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get("publicTime") / 1000))
                print(item)
                items.append(item)
            time.sleep(5)
            print()
            print()
            print()

    def start(self):
        for page in range(1, 4):
            list_url = self.format_url % page
            print(list_url)
            self.get_list_items(list_url)


if __name__ == "__main__":
    suhu = SuhuFinance()
    suhu.start()

