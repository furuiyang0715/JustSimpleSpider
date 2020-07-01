# 模拟返回搜狗搜索的内容

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}

base_url = 'https://www.sogou.com/web?query={}'
for key_word in ['语文', '数学', '音乐']:
    resp = requests.get(base_url.format(key_word), headers=headers)
    print(resp.text)
