import requests
from fake_useragent import UserAgent
import re

ua = UserAgent()
# print(ua.random)


def ceshi(ip):
    url = "http://2019.ip138.com/ic.asp"
    headers = {
        'User-Agent': ua.random
    }
    proxies = {
        "http": "http://" + ip,
    }
    try:
        resp = requests.get(url=url, headers=headers, proxies=proxies, timeout=2, allow_redirects=False)
        if '<body style="margin:0px"><center>' in resp.text:
            ip1 = re.findall('<body style="margin:0px"><center>.*\[(.*?)\].*</center>', resp.text)[0]
            if ip1 != '42.120.74.109':
                print("ip可用", ip1)
                # file_save.write(ip + '\n')
            else:
                print("ip是透明的")
        else:
            print("errer")
    except Exception as e:
        print("异常", e)


if __name__ == '__main__':
    ip = '106.75.140.177:8888'
    ceshi(ip)
