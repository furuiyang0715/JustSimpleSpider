import requests

headers = {
    # b":authority": "www.taoguba.com.cn",
    # b":method": "GET",
    # b":path": "/quotes/getStockHeat?stockCode=sz300150&pageNo=1&perPageNum=20&isOpen=false",
    # b":scheme": "https",
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'cookie': '''JSESSIONID=f45d82d9-8811-46e2-ad9d-b51966a460cc; Hm_lvt_cc6a63a887a7d811c92b7cc41c441837=1594448378; UM_distinctid=1733c8778dd26a-07b2c169f81009-31617402-1fa400-1733c8778dea53; CNZZDATA1574657=cnzz_eid%3D512829114-1594445650-%26ntime%3D1594445650; __gads=ID=35d9e7fe87d53615:T=1594448473:S=ALNI_MYwpLq-g-JJX1Wc5jpH6fLV_w04wg; Hm_lpvt_cc6a63a887a7d811c92b7cc41c441837=1594448701''',
    'pragma': 'no-cache',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}


url = 'https://www.taoguba.com.cn/quotes/getStockHeat?stockCode=sz300150&pageNo=1&perPageNum=20&isOpen=false'
resp = requests.get(url, headers=headers)
print(resp)
