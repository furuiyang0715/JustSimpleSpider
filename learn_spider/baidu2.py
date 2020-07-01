import requests
import json
import sys

class FanyiSpider(object):

    def __init__(self, word):
        # 检测语言URL
        self.detect_url = 'http://fanyi.baidu.com/langdetect'
        # 准备翻译的URL
        self.trans_url = 'http://fanyi.baidu.com/basetrans'
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36'
        }
        # 要翻译的内容
        self.word = word

    def get_data_from_url(self, url, data):
        '''根据URL,获取响应数据'''
        response = requests.post(url, data=data, headers=self.headers)
        return response.content

    def run(self):
        '''程序入口'''
        # 检查当前要翻译的语言类型
        # 准备检查当前语言类型的URL
        # http://fanyi.baidu.com/langdetect
        #      2. 数据: query: 你
        data = {'query': self.word}
        #      3. 发送请求获取响应数据
        # {"error":0,"msg":"success","lan":"zh"}
        rs = self.get_data_from_url(self.detect_url, data)
        print(rs)
        sys.exit(0)
        rs = json.loads(rs)
        # 翻译
        #  准备翻译URL
        # http://fanyi.baidu.com/basetrans
        # 准备翻译数据
        # query: 你
        # from: zh
        # to: en
        data['from'] = rs['lan']
        # 格式: 结果1 if 条件 else 结果2
        # 如果条件成立就是结果1 否则就是结果2
        data['to'] = 'en' if rs['lan'] == 'zh' else 'zh'
        # 发送请求, 获取响应
        rs = self.get_data_from_url(self.trans_url, data)
        # print(rs)
        # 解析数据, 获取翻译结果
        rs = json.loads(rs)
        print(rs['trans'][0]['dst'])


if __name__ == '__main__':
    # 获取命令行上python 文件名  数据
    # print(sys.argv)
    word = sys.argv[1]
    fy = FanyiSpider(word)
    fy.run()
