import pprint

import requests
import jsonpath
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'cookie': 'user_trace_token=20200701164425-11585c7a-bb77-11ea-b394-5254002dd181; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22173098c92529c5-07d4743ebda38a-31617402-2073600-173098c9253ca9%22%2C%22%24device_id%22%3A%22173098c92529c5-07d4743ebda38a-31617402-2073600-173098c9253ca9%22%7D; sajssdk_2015_cross_new_user=1; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1593593074; _ga=GA1.2.548023287.1593593074; _gid=GA1.2.1790011005.1593593074; LGSID=20200701164434-a3d6e2e2-8858-4a83-b600-1614212fa85a; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fsec.lagou.com%2Fverify.html%3Fe%3D2%26f%3Dhttps%3A%2F%2Fwww.lagou.com%2Flagouhtml%2Fa44.html; PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html; LGUID=20200701164434-45743fc6-7c2a-42d7-949d-a7f378294978; gate_login_token=ed2d3d5fc6b7635f7be324cc77d2512fa1c7b9edf0542ed287a168fcd079b05b; LG_LOGIN_USER_ID=a2b0536a4e1c2beaf991e3a32e7df4a91b3c8fab4ccb065c347fce98de83c320; LG_HAS_LOGIN=1; _putrc=CF6B96FD96431187123F89F2B170EADC; JSESSIONID=ABAAAECAAEBABII44CC98C22F16DA8B0ED5281B86DBDA96; login=true; unick=%E7%AC%A6%E7%91%9E%E9%98%B3; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=26; privacyPolicyPopup=false; index_location_city=%E5%B9%BF%E5%B7%9E; WEBTJ-ID=20200701164534-173098d7c755e0-0db5439465fd19-31617402-2073600-173098d7c76471; RECOMMEND_TIP=true; _gat=1; X_HTTP_TOKEN=7d0f6847c6d8944d3413953951fe1c8b0418c2b022; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1593593144; LGRID=20200701164543-a579f46c-4426-4d28-898b-e0f2b42ca8fb'
}


url = 'http://www.lagou.com/lbs/getAllCitySearchLabels.json'
html = requests.get(url, headers=headers).text

# 把json格式字符串转换成python对象
jsonobj = json.loads(html)

# print(pprint.pformat(jsonobj))

# # 从根节点开始，匹配name节点
citylist = jsonpath.jsonpath(jsonobj, '$..name')
print(citylist)

# fp = open('city.json', 'w')
#
# content = json.dumps(citylist, ensure_ascii=False)
#
# fp.write(content.encode('utf-8'))
# fp.close()
