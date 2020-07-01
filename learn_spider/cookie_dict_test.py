# 将 cookie 对象转换为字典
import requests

# 1、reqeusts.util.dict_from_cookiejar  把cookie对象转化为字典
url = 'http://www.baidu.com'
response = requests.get(url)
print(response.cookies)
cookjar = response.cookies

# 将cookjar对象转换成字典类型数据
dict_cookies = requests.utils.dict_from_cookiejar(cookjar)
print(dict_cookies)

# 将字典类型数据转换成cookjar对象
print(requests.utils.cookiejar_from_dict(dict_cookies))

response = requests.get("http://www.baidu.com?kw='经传多赢'")
print(response.url)    # http://www.baidu.com/?kw='%E7%BB%8F%E4%BC%A0%E5%A4%9A%E8%B5%A2'

# 我们直接打印响应的URL都是经过URL编码后的字符串, 如果我们想看到原始URL该怎么办呢?
# 我们可以使用URL解码, 把字符串进行还原
url = requests.utils.unquote(response.url)
print(url)
# 如果需要对URL进行编码可以使用quote
encode_url = requests.utils.quote(url)
print(encode_url)
# print(requests.get(encode_url))
