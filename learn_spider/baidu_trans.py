'''实现百度中英文翻译'''

# 准备检查当前语言类型的URL
# http://fanyi.baidu.com/langdetect
# 翻译接口
# http://fanyi.baidu.com/basetrans
import requests


class BaiduTrans(object):

    def __init__(self):
        self.langdetect_url = 'http://fanyi.baidu.com/langdetect'
        self.trans_url = 'http://fanyi.baidu.com/basetrans'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36'
        }

    def detect_lang(self, ipt: str):
        resp = requests.post(self.langdetect_url, data={"query": ipt}, headers=self.headers)
        print(resp)
        print(resp.text)


if __name__ == "__main__":
    print("\u672a\u77e5\u9519\u8bef")
    bd = BaiduTrans()
    bd.detect_lang("我")
