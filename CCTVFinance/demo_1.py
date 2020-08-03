import requests

url = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/economy_1.jsonp?cb=economy'
resp = requests.get(url)
if resp.status_code == 200:
    body = resp.text
    print(body)