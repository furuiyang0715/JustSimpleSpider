import requests as req

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': '_trs_uv=k64w3spl_6_bt2t; AD_RS_COOKIE=20080917; _trs_ua_s_1=k6s0oxq1_6_dqaj',
    'Host': 'www.stats.gov.cn',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
}

url = "http://www.stats.gov.cn/tjsj/zxfb/index.html"

ret = req.get(url, headers=headers)
text = ret.text.encode("ISO-8859-1").decode("utf-8")
print(text)

