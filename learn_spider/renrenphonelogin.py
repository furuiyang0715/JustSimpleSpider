'''
window.login = {
    init: function() {
        initREM(),
        this.resetHref(),
        this.formSubmit(),
        login1()
    },
    resetHref: function() {
        window.c1 = getQueryString("c1");
        for (var e = $(".js-register"), t = 0; t < e.length; t++)
            e[t].href = "http://activity.renren.com/livecell/reg?c1=" + c1
    },
    formSubmit: function() {
        var e, t = {};
        $(".login").addEventListener("click", function() {
            t.phoneNum = $(".phonenum").value,
            t.password = $(".password").value,
            e = loginValidate(t),
            t.c1 = c1 || 0,
            e.flag ? ajaxFunc("get", "http://activity.renren.com/livecell/rKey", "", function(e) {
                var n = JSON.parse(e).data;
                if (0 == n.code) {
                    t.password = t.password.split("").reverse().join(""),
                    setMaxDigits(130);
                    var o = new RSAKeyPair(n.e,"",n.n)
                      , r = encryptedString(o, t.password);
                    t.password = r,
                    t.rKey = n.rkey
                } else
                    toast("公钥获取失败"),
                    t.rKey = "";
                ajaxFunc("post", "http://activity.renren.com/livecell/ajax/clog", t, function(e) {
                    var e = JSON.parse(e).logInfo;
                    0 == e.code ? location.href = localStorage.getItem("url") || "" : toast(e.msg || "登录出错")
                })
            }) : toast(e.msg)
        })
    }
};
'''
import pprint
import sys

'''
安装js2py: pip install js2py
使用js2py的步骤:
获取执行js环境: context = js2py.EvalJs()
使用context来执行js: js.execute(js_str)
向context中添加数据 context.xx = oo
获取context中数据 context.xx
js2py的特点: 就是慢 

renren 手机端的登录逻辑： 
(1) 去请求某个接口 获得一个 rkey 的值
(2) 需要对密码进行加密: 加密需要先进行反转 再进行 rsa 加密 
(3) 最后向"http://activity.renren.com/livecell/ajax/clog" 发送 post 登录请求
请求数据为： 
phoneNum 
password （加密后产生的） 
c1 
rKey (rkey请求获得的)

'''

import requests
import json
import js2py


class RenrenLoginSpider(object):
    def __init__(self):
        # 获取session对象
        self.session = requests.session()
        # 给session设置请求头
        self.session.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36"
        }
        # 最终登录的 URL
        self.clog_url = 'http://activity.renren.com/livecell/ajax/clog'
        # 请求 rkey 的URL
        self.rkey_url = 'http://activity.renren.com/livecell/rKey'
        # 创建执行 js 的环境
        self.context = js2py.EvalJs()

    def get_data_from_url(self, url, data=None):
        '''发送请求, 获取二进制数据'''
        if data is None:
            response = self.session.get(url)
        else:
            response = self.session.post(url, data=data)
        return response.content

    def load_js_from_url(self, url):
        '''通过URL执行js,也就是加载js'''
        js = self.get_data_from_url(url).decode()
        self.context.execute(js)

    def run(self):
        # 获取session对象
        # 设置请求头
        # i.setRequestHeader("X-Requested-With", "XMLHttpRequest"),
        # i.setRequestHeader("Content-Type", "application/x-www-form-urlencoded"
        # 发送rkey请求, 获取加密需要使用的数据
        # 准备URL: http://activity.renren.com/livecell/rKey
        # 发送请求, 获取数据
        result = self.get_data_from_url(self.rkey_url)
        # 解析数据
        n = json.loads(result)['data']
        print(pprint.pformat(n))

        # 使用js2py创建js的执行环境
        # 让js执行环境加载相关js的文件
        self.load_js_from_url('http://s.xnimg.cn/a85738/wap/mobile/wechatLive/js/RSA.js')
        self.load_js_from_url('http://s.xnimg.cn/a85738/wap/mobile/wechatLive/js/BigInt.js')
        self.load_js_from_url('http://s.xnimg.cn/a86836/wap/mobile/wechatLive/js/celllog.js')
        self.load_js_from_url('http://s.xnimg.cn/a85738/wap/mobile/wechatLive/js/Barrett.js')

        # 给js执行环境设置需要的数据
        self.context.t = {
            'phoneNum': '15626046299',
            'password': '044610Fa'
        }

        self.context.n = n
        # 生成登录数据js代码
        js = '''
            t.password = t.password.split("").reverse().join(""),
            setMaxDigits(130);
            var o = new RSAKeyPair(n.e,"",n.n)
            , r = encryptedString(o, t.password);
            t.password = r,
            t.rKey = n.rkey
        '''

        # 执行js, 获取发送登录需要的数据
        self.context.execute(js)
        print(self.context.t)
        # 准备登录URL: http://activity.renren.com/livecell/ajax/clog
        result = self.get_data_from_url(self.clog_url, data=self.context.t.to_dict())
        # 发送登录
        # 使用登录的session访问其他资源
        result = json.loads(result)
        print(result)
        data = self.get_data_from_url('http://activity.renren.com/myprofile')
        print(data.decode())


if __name__ == '__main__':
    rrls = RenrenLoginSpider()
    rrls.run()

