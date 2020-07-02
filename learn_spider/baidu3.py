import requests
from lxml import etree
import json


class TieBaSpider(object):
    """百度贴吧爬虫"""
    def __init__(self, name):
        self.name = name
        self.list_url_pattern = "http://tieba.baidu.com/mo/q----,sz@320_240-1-3---/m?kw=" + name + "&pn={}"
        self.host = "http://tieba.baidu.com"
        self.pre_url = "http://tieba.baidu.com/mo/q---8DC83EB65C86E38C9EC4A227050C8970%3AFG%3D1-sz%40320_240%2C-1-3-0--2--wapp_1523749569931_549/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Mobile Safari/537.36"
        }

    def get_page_html(self, url):
        """获取页面响应的 content"""
        response = requests.get(url, headers=self.headers)
        return response.content

    def get_content_list(self, page_html):
        """获取标题,URL,详情页的图片"""
        page_element = etree.HTML(page_html)
        divs = page_element.xpath("//div[contains(@class, 'i')]")
        content_list = []
        for div in divs:
            dic = dict()
            dic['title'] = div.xpath("./a/text()")[0] if len(div.xpath("./a/text()")) != 0 else None
            dic['url'] = self.host + div.xpath("./a/@href")[0] if len(div.xpath("./a/@href")) else None
            images = self.get_images(dic['url'])
            dic["images"] = [requests.utils.unquote(image).split("&src=")[-1] for image in images]
            content_list.append(dic)
        return content_list

    def get_images(self, detail_url):
        #    - 3.1 获取详情页的URL
        #    - 3.2 给URL发送请求,获取内容
        detail_html = self.get_page_html(detail_url)
        #    - 3.3 提取图片的URL,和下一页URL
        detail_element = etree.HTML(detail_html)
        images = detail_element.xpath("//img[@class='BDE_Image']/@src")
        next_detail_urls = detail_element.xpath("//a[text()='下一页']/@href")
        # print(next_detail_urls)
        if len(next_detail_urls) != 0:
            next_detail_url = self.pre_url + next_detail_urls[0]
            images += self.get_images(next_detail_url)  # 每调用一次就会返回下一页所有图片的URL的地址列表
        #    - 3.4 循环3.2-3.3
        return images

    def save_conent_list(self, content_list):
        """将爬取到的内容保存到文件中"""
        with open(self.name + ".txt", 'a', encoding="utf8") as f:
            for content in content_list:
                json.dump(content, f, ensure_ascii=False)
                f.write("\n")

    def run(self):
        # 0. 定义变量 pn=0
        pn = 0
        while True:
            # 1. 准备URL
            list_url = self.list_url_pattern.format(pn)
            print(list_url)
            # 2. 发送请求获取内容
            page_html = self.get_page_html(list_url)
            print(page_html)
            # print(type(page_html))    # bytes
            # 3. 根据内容提取数据
            content_list = self.get_content_list(page_html)
            # print(content_list)
            # for content in content_list:
            #     print(content)
            # 4. 保存内容
            self.save_conent_list(content_list)
            # 5. pn 序号递增20, 循环1-4
            pn += 20
            if len(content_list) < 20:
                break


if __name__ == '__main__':
    tbs = TieBaSpider("做头发")
    tbs.run()
