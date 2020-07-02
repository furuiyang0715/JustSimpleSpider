import sys

import requests
from lxml import etree, html
import json
import re


class QiuBaiSpider(object):
    """嗅事百科爬虫
    需求: 提取糗百中热门主题中所有段子信息,每个段子包含发送人头像URL,昵称,性别,段子内容, 好笑数,评论数
    """
    def __init__(self):
        self.url_pattern = "https://www.qiushibaike.com/8hr/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        }

    def get_url_list(self):
        """要爬取的url列表页"""
        return [self.url_pattern.format(i) for i in range(1, 14)]

    def get_html(self, url):
        """获取要爬取的页面的 content 信息"""
        response = requests.get(url, headers=self.headers)
        return response.content

    # def get_content_list(self, html):
    #     """解析页面数据"""
    #     page_elment = etree.HTML(html)
    #     divs = page_elment.xpath("//div[@class='recmd-right']")
    #     content_list = []
    #     for div in divs:
    #         user_head = div.xpath(".//div[@class = 'author clearfix']//img/@src")
    #         user_head = user_head[0] if len(user_head) != 0 else None
    #         user_name = div.xpath(".//div[@class = 'author clearfix']//h2/text()")
    #         user_name = user_name[0] if len(user_name) !=0 else None
    #         user_gender = div.xpath(".//div[starts-with(@class, 'articleGender')]/@class")
    #         user_gender = re.findall("articleGender\s*(\\w+)Icon",user_gender[0])[0] if len(user_gender) != 0 else None
    #         content = div.xpath(".//div[@class='content']/span//text()")
    #         content = content[0] if len(content) != 0 else None
    #         vote = div.xpath(".//span[@class='stats-vote']/i/text()")
    #         vote = vote[0] if len(vote) !=0 else None
    #         comments = div.xpath(".//span[@class='stats-comments']//i/text()")
    #         comments = comments[0] if len(comments) !=0 else None
    #         dic = {"user_head": user_head,
    #                "user_name": user_name,
    #                "user_gender": user_gender,
    #                "content": content,
    #                "vote": vote,
    #                "comments": comments,
    #                }
    #         print(dic)
    #         content_list.append(dic)
    #     return content_list

    def get_content_list(self, text):
        doc = html.fromstring(text)
        # //*[@id="content"]/div/div[2]/div
        lis = doc.xpath(".//div[@class='recommend-article']/ul/li")
        # print(lis)     # 发送人头像URL,昵称,性别,段子内容, 好笑数,评论数
        '''
        <li class="item typs_video" id="qiushi_tag_123269490">
            <a class="recmd-left video" href="/article/123269490" rel="nofollow" target="_blank" onclick="_hmt.push(['_trackEvent','web-list-video','chick'])">
                <img src="//qiubai-video-web.qiushibaike.com/51SN0556L0Z1U930_hd.jpg?imageView2/1/w/150/h/112" alt="糗友们，这个怎么说？">
                <div class="recmd-tag">0:11</div>
            </a>
            <div class="recmd-right">
                <a class="recmd-content" href="/article/123269490" target="_blank" onclick="_hmt.push(['_trackEvent','web-list-user','chick'])">糗友们，这个怎么说？</a>
                <div class="recmd-detail clearfix">
                    <div class="recmd-num">
                        <span>211</span>
                        <span>好笑</span>
                        <span>·</span>
                        <span>2</span>
                        <span>评论</span>
                    </div>
            
                    <a class="recmd-user">
                        <img src="//pic.qiushibaike.com/system/avtnew/4408/44087374/thumb/20200611150249.jpg?imageView2/1/w/50/h/50" alt="缘来～是你啊">
                        <span class="recmd-name">缘来～是...</span>
                    </a>
                </div>
            </div>
        </li>
        '''
        for li in lis:
            # 发送人头像URL
            user_img = li.xpath(".//a[@class='recmd-user']/img/@src")[0].lstrip("//")
            print(user_img)
            # 昵称
            user_name = li.xpath(".//span[@class='recmd-name']")[0].text_content()
            print(user_name)
            # 性别
            # 段子内容
            title = li.xpath(".//a[@class='recmd-content']")[0].text_content()
            print(title)
            # 好笑数
            read_info = li.xpath(".//div[@class='recmd-num']/span")
            vote = int(read_info[0].text_content())
            comments = int(read_info[-2].text_content())
            print(vote)
            print(comments)

            # 评论数

    def sav_conent_list(self, content_list):
        """保存数据到文件中"""
        with open("qiubai.txt", 'a', encoding='utf-8') as f:
            for conent in content_list:
                json.dump(conent, f, ensure_ascii=False)
                f.write("\n")

    def run(self):
        url_list = self.get_url_list()
        print(url_list)
        for url in url_list:
            print(url)
            html = self.get_html(url)
            text = html.decode()
            content_list = self.get_content_list(text)
            # self.sav_conent_list(content_list)

            print()
            print()
            print()


if __name__ == '__main__':
    qs = QiuBaiSpider()
    qs.run()
