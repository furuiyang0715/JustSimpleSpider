import requests as re

url = 'http://webapi.cninfo.com.cn/#/aidetail?type=sysapi%2Fp_sysapi1128&scode=009018'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Cookie': 'pgv_pvid=6020356972; __qc_wId=209; Hm_lvt_489bd07e99fbfc5f12cbb4145adb0a9b=1585189755; Hm_lpvt_489bd07e99fbfc5f12cbb4145adb0a9b=1585203089; codeKey=b6a504fe60',
    'Host': 'webapi.cninfo.com.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://webapi.cninfo.com.cn/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
}

page = re.get(url, headers=headers)
print(page.encoding)
print(page.text.encode("ISO-8859-1").decode("utf-8"))
