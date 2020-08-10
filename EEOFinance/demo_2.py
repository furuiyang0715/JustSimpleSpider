# 请求主页数据
import requests

index_url = 'http://www.eeo.com.cn/shangyechanye/'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'PHPSESSID=7avdv48orrl42d4s323eae4dn5; acw_tc=2760775215970417166888855e8f887a018cbf5f73aab22ec8d9ae03f7e2b4; SERVERID=adeed77a8e607bd6b1d16fea05016e81|1597041716|1597041716',
    'Host': 'www.eeo.com.cn',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
}

resp = requests.get(index_url, headers=headers)
if resp and resp.status_code == 200:
    body = resp.text.encode("ISO-8859-1").decode("utf-8")
    print(body)
else:
    print(resp)
