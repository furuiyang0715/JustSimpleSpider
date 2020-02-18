import requests

headers = {
'Accept': 'application/json, text/javascript, */*; q=0.01',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
'Content-Length': '0',
'Cookie': '__qc_wId=726; pgv_pvid=6020356972; Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1581945588; codeKey=ce7a9a719b; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1582016401',
'Host': 'webapi.cninfo.com.cn',
'mcode': 'MTU4MjAxNjYzMw==',
'Origin': 'http://webapi.cninfo.com.cn',
'Pragma': 'no-cache',
'Referer': 'http://webapi.cninfo.com.cn/',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest',

}


url = "http://webapi.cninfo.com.cn//api/sysapi/p_sysapi1128"
resp = requests.post(url, headers=headers)
print(resp)
