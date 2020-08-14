import json
import re
import sys
import time

import requests

# url = 'http://www.eeo.com.cn/shangyechanye/'    # 商业产业
#
# resp = requests.get(url)
# if resp and resp.status_code == 200:
#     body = resp.text
#     print(body)

# api_url = 'http://app.eeo.com.cn/?app=wxmember&controller=index&action=getMoreArticle\
# &jsoncallback=jsonp1597038838052\
# &catid=3572\
# &allcid=397442,397434,397412,397399,397393,397282,397264,397222,397116,397115,397015,397011,397008,397007,397006,397013\
# &page=\
# &_=1597038933283'

# 商业产业
api_url = 'http://app.eeo.com.cn/?app=wxmember&controller=index&action=getMoreArticle\
&jsoncallback=jsonp{}\
&catid=3572\
&allcid=397442,397434,397412,397399,397393,397282,397264,397222,397116,397115,397015,397011,397008,397007,397006,397013\
&page=0\
&_={}'.format(int(time.time() * 1000), int(time.time() * 1000))

# 财经
api_url = 'http://app.eeo.com.cn/?app=wxmember&controller=index&action=getMoreArticle\
&jsoncallback=jsonp{}\
&catid=3548\
&allcid=399177,399154,399124,399092,399076,399077,399071,399018,398686,398574,398450,398445,398374,398167,398165,398106\
&page=0\
&_={}'.format(int(time.time() * 1000), int(time.time() * 1000))

# 地产
api_url = 'http://app.eeo.com.cn/?app=wxmember&controller=index&action=getMoreArticle\
&jsoncallback=jsonp{}\
&catid=3583\
&allcid=399218,399108,399085,398868,398630,398628,398561,398355,398341,398534,398380,398470,398465,398381,398405,398370\
&page=0\
&_={}'.format(int(time.time() * 1000), int(time.time() * 1000))


headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'acw_tc=276077d915970380735073656eb4f9ebda87734f914d4ace3238985ebfe3ac; PHPSESSID=7avdv48orrl42d4s323eae4dn5; SERVERID=7a130e5b09ba7fb9ae243186f7f131d1|1597038838|1597038073',
    'Host': 'app.eeo.com.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://www.eeo.com.cn/shangyechanye/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
}


resp = requests.get(api_url, headers=headers)
if resp and resp.status_code == 200:
    body = resp.text
    body = body.encode("ISO-8859-1").decode("utf-8")
    print(body)
    data_str = re.findall('jsonp\d{13}\((.*)\)', body)[0]
    print(data_str)
    datas = None
    try:
        datas = json.loads(data_str)
    except:
        print("error")
    else:
        print(datas)
    if not datas:
        sys.exit(0)

    articles = datas.get("article")
    for one in articles:
        print(one)

        # print(one.keys())
        # dict_keys(['contentid', 'pv', 'catid', 'title', 'thumb', 'url', 'name', 'curl', 'comments',
        # 'published', 'description', 'author', 'spaceid', 'differTime', 'catname', 'caturl'])

        # 发布的时间戳: published
        # 最后修改时间: differTime
        pub_ts = int(one.get("published"))
        pub_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pub_ts))
        print(pub_date)
        print(one.get("differTime"))
        print()

