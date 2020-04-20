import threading
import time
import csv
import os
import traceback

import requests
import threadpool
from bs4 import BeautifulSoup

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


def fetch_keywords(start, end):
    items = []
    for i in range(start, end+1):
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
                # 百度百科错误页
            except:
                item['KeyWord'] = word
                print(item)
                items.append(item)
            time.sleep(0.1)
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


def spider(_start):
    csv_columns = ['KeyId', 'KeyWord']
    items = fetch_keywords(_start, _start+interval-1)
    current_path = os.getcwd()
    os.makedirs(current_path + "/csv/csv_{}_{}".format(START*interval+1, END*interval), exist_ok=True)
    csv_file = current_path + "/csv/csv_{}_{}/key_words_{}_{}.csv".format(START*interval+1, END*interval, _start, _start + interval - 1)
    write_dicttocsv(csv_file, csv_columns, items)


now = lambda: time.time()


def main():
    """
    range(0, 10)   0-9  1-10000
    range(10, 20) 10-19 10001-20000
    range(20, 30) 20-29 20001-30000
    range(30, 40) 30-39 30001-40000
    ...

    """
    t1 = now()
    _list = [i*interval+1 for i in range(START, END)]
    _pool = threadpool.ThreadPool(4)
    _requests = threadpool.makeRequests(spider, _list)
    [_pool.putRequest(req) for req in _requests]
    _pool.wait()
    print("用时: {} 秒".format(now() - t1))


interval = 1000
START = int(os.environ.get("START", 70))
END = int(os.environ.get("END", 80))

main()


'''
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/baidukeyword:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/baidukeyword:v1
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/baidukeyword:v1

# local 
docker run -itd --name bdkw \
-v /Users/furuiyang/gitzip/JustSimpleSpider/baidu:/baidu \
--env START=80 \
--env END=90 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/baidukeyword:v1
'''
