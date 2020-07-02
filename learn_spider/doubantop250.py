'''
接下来我们通过豆瓣电影top250的页面来练习上述语法：https://movie.douban.com/top250

选择所有的h1下的文本
//h1/text()
获取所有的a标签的href
//a/@href
获取html下的head下的title的文本
/html/head/title/text()
获取html下的head下的link标签的href
/html/head/link/@href
'''

import requests
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}
url = 'https://movie.douban.com/top250'
resp = requests.get(url, headers=headers)
# print(resp)
body = resp.text
# print(body)
doc = html.fromstring(body)
# 选择所有的h1下的文本
ret1 = doc.xpath("//h1/text()")
print(ret1)

# 获取所有的a标签的href
ret2 = doc.xpath("//a/@href")
print(ret2)

# 获取html下的head下的title的文本
ret3 = doc.xpath('/html/head/title/text()')
print(ret3)

# 获取html下的head下的link标签的href
ret4 = doc.xpath("/html/head/link/@href")
print(ret4)



'''
<li>
    <div class="item">
        <div class="pic">
            <em class="">23</em>
            <a href="https://movie.douban.com/subject/1849031/">
                <img width="100" alt="当幸福来敲门" src="https://img1.doubanio.com/view/photo/s_ratio_poster/public/p1312700628.jpg" class="">
            </a>
        </div>
        <div class="info">
            <div class="hd">
                <a href="https://movie.douban.com/subject/1849031/" class="">
                    <span class="title">当幸福来敲门</span>
                            <span class="title">&nbsp;/&nbsp;The Pursuit of Happyness</span>
                        <span class="other">&nbsp;/&nbsp;寻找快乐的故事(港)  /  追求快乐</span>
                </a>


                    <span class="playable">[可播放]</span>
            </div>
            <div class="bd">
                <p class="">
                    导演: 加布里尔·穆奇诺 Gabriele Muccino&nbsp;&nbsp;&nbsp;主演: 威尔·史密斯 Will Smith ...<br>
                    2006&nbsp;/&nbsp;美国&nbsp;/&nbsp;剧情 传记 家庭
                </p>

                
                <div class="star">
                        <span class="rating45-t"></span>
                        <span class="rating_num" property="v:average">9.1</span>
                        <span property="v:best" content="10.0"></span>
                        <span>1103516人评价</span>
                </div>

                    <p class="quote">
                        <span class="inq">平民励志片。 </span>
                    </p>
            </div>
        </div>
    </div>
</li>
'''

