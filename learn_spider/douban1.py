# 1. 准备URL
#      - 准备一个获取豆瓣热映电影信息的json数据的URL
#      - 如果电脑web版没有找到json数据, 可以尝试使用手机版
#       https://m.douban.com/rexxar/api/v2/subject_collection/movie_showing/items?start=0&count=18&loc_id=108288
# 豆瓣电影json数据对用的URL
import json

import requests

douban_movie_url = "https://m.douban.com/rexxar/api/v2/subject_collection/movie_showing/items?start=0&count=18&loc_id=108288"

# 2. 根据这个URL,发送请求获取热映电影json数据
# 2.1 直接发送请求,获取的数据是错误的,但是我们浏览器确实可以获取正确数据
# 2.2 我们在发送请求的时候,模拟浏览器,要模拟更像一点. 增加请求头相关信息
# 定义请求头
headers = {
    "Referer": "https://m.douban.com/movie/nowintheater?loc_id=108288",
    "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36"
}

response = requests.get(douban_movie_url, headers=headers)
# 通过response获取我们要的json数据
json_str = response.content.decode()
# print(json_str)
# 3. 解析数据(json) -> 把json字符串 -> python数据类型
movie_items = json.loads(json_str)
# print(movie_items)
# 4. 保存数据
with open("douban_movie.json", 'w', encoding='utf8') as f:
    json.dump(movie_items, f, ensure_ascii=False, indent=4)
