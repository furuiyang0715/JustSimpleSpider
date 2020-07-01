import requests

url = 'https://www.sina.com.cn/'
resp = requests.get(url)

print(resp.encoding)


# print(resp.text)


# print(resp.content.decode())
