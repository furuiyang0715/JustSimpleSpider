import sys
import time
import csv
import os
import traceback

import requests
from bs4 import BeautifulSoup

now = lambda: time.time()

base_url = 'http://baike.baidu.com/view/{}.html'
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "BAIDUID=EB6F3A7C18E88C30D3FA7E1CE33D3A76:FG=1; H_WISE_SIDS=139561_141143_139203_139419_139405_135846_141002_139148_138471_138655_140142_133995_138878_137985_140174_131246_132551_141261_138165_107315_138883_140259_140632_140202_139297_138585_139625_140113_136196_140591_140324_140578_133847_140793_134047_131423_140822_140966_136537_139577_110085_140987_139539_127969_140593_140421_140995_139407_128196_138313_138426_141194_138941_139676_141190_140596_138755_140962; BIDUPSID=EB6F3A7C18E88C30D3FA7E1CE33D3A76; PSTM=1581310449; BDUSS=zRoelBjR1ZSdlNRanFCSk56dE13aWJqcERrWW01WDhUVVJpaGxadFNHRW85SE5jQVFBQUFBJCQAAAAAAAAAAAEAAAAllGSYRW5qb2xyYXNfZnV1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAChnTFwoZ0xcQ; cflag=13%3A3; ZD_ENTRY=bing; BKWPF=3; Hm_lvt_55b574651fcae74b0a9f1cf9c8d7c93a=1586931950,1586932055; Hm_lpvt_55b574651fcae74b0a9f1cf9c8d7c93a=1587361584",
    "Host": "baike.baidu.com",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
}


def fetch_one(i):
    item = dict()
    item['KeyId'] = i
    url = base_url.format(i)
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        page = resp.text
        soup = BeautifulSoup(page, features='lxml')
        word = soup.find('h1').get_text()
        try:
            error_info = word.encode("ISO-8859-1").decode("utf-8")
        except:
            item['KeyWord'] = word
            print(item)
            return item
        else:
            print("百度百科错误页")
    else:
        raise


def fetch_keywords(start, end):
    lst = []
    items = []
    for i in range(start, end+1):
        try:
            item = fetch_one(i)
        except:
            lst.append(i)
        else:
            if item:
                items.append(item)
    print(lst)
    return items


def write_dicttocsv(csv_file, csv_columns, dict_data):
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        traceback.print_exc()
        print("写入错误")


def simple_spider(write_file, start, end):
    items = fetch_keywords(start, end)
    print(len(items))
    csv_columns = ['KeyId', 'KeyWord']
    write_dicttocsv(write_file, csv_columns, items)


start = int(os.environ.get("START", 390001))
end = int(os.environ.get("END", 400000))


if __name__ == "__main__":
    _dir = "/bbd/csv/{}_{}".format(start, end)
    os.makedirs(_dir, exist_ok=True)
    for i in range(start, end, 1000):
        t1 = now()
        print(i, i+1000-1)
        file = os.path.join(_dir, f"key_words_{i}_{i+1000-1}.csv")
        simple_spider(file, i, i+1000-1)
        print("耗时:{} s".format(now() - t1))


'''
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/bd:v1 .

sudo docker run -itd --name demo_1455000_1470000 \
-v /Users/furuiyang/gitzip/JustSimpleSpider/bbd:/bbd \
--env START=1455000 \
--env END=1470000 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/bd:v1
'''

'''
sudo docker run -itd --name demo_1594_1595 \
-v /home/furuiyang/bbd:/bbd \
--env START=15940001 \
--env END=15950000 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/bd:v1
'''