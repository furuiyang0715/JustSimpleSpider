# 从上交所的爬虫文件中获取到信息
import traceback

import requests

file_url = '''http://biz.sse.com.cn//report/rzrq/dbp/zqdbp20210222.xls'''

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
}

# (1) 下载文件
try:
    resp = requests.get(file_url, timeout=3, headers=headers)
except:
    traceback.print_exc()
    resp = None

if resp and resp.status_code == 200:
    content = resp.content
    with open('zqdbp20210222.xls', 'wb') as f:
        f.write(content)
else:
    print(resp)

# (2) 解析文件数据

# (3) 整理并且存入数据库


