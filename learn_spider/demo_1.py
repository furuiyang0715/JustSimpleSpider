# str 与 bytes 之间的相互转换
s = '中国'
print(s)

ret1 = s.encode()
print(ret1)

ret2 = s.encode("utf-8")
print(ret2)

print(ret1 == ret2)

ret3 = ret1.decode()
print(ret3)

ret4 = ret2.decode("utf-8")
print(ret3 == ret4)

_gbk = s.encode("GBK")
print(_gbk)
ret5 = _gbk.decode("GBK")
print(ret5)


# requests 的请求头以及响应头
import requests

url = 'http://www.baidu.com'
resp = requests.get(url)
print(resp)
# 请求头
print(resp.request.headers)
# 响应头
print(resp.headers)
# 网页的二进制数据
content = resp.content
print(content)
# 网页数据
text = content.decode()
print(text)

# 使用 requests 下载一张图片保存到本地
img_url = 'http://n1-q.mafengwo.net/s11/M00/6A/39/wKgBEFqfiOGAQIfFAAEiFjXBMNM09.jpeg?imageMogr2%2Fthumbnail%2F%21690x450r%2Fgravity%2FCenter%2Fcrop%2F%21690x450%2Fquality%2F90%7Cwatermark%2F1%2Fimage%2FaHR0cDovL2IxLXEubWFmZW5nd28ubmV0L3MxMS9NMDAvNDQvOUIvd0tnQkVGc1A1UnlBRHY3cEFBQUhaWlVQUmxROTkwLnBuZw%3D%3D%2Fgravity%2FSouthEast%2Fdx%2F10%2Fdy%2F11'
resp = requests.get(img_url)
print(resp)
content = resp.content
with open("kl.png", "wb") as f:
    f.write(content)

# 为请求加上请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}
resp = requests.get("http://www.baidu.com", headers=headers)
print(resp.text)

