"""
使用 cookie 登录的三种方式

以登录人人网个人主页 为例子

"""
import pprint

import requests

cookie_str = 'anonymid=kc2xpybx2fwm1o; depovince=GW; jebecookies=d14fe2e4-d70c-4cae-a163-f9d9b5aba2e4|||||; _r01_=1; taihe_bi_sdk_uid=a66f3793a2b186fc6756a5efa45de983; taihe_bi_sdk_session=9212b690413cd576484d06c078cc99be; ick_login=f56e5e4f-40a6-435d-aa14-156ebb34ee86; _de=82D006EDB0340D0076B255B13038CCD8; p=c230f61db04fac2548054d31f157729e8; first_login_flag=1; ln_uact=15626046299; ln_hurl=http://head.xiaonei.com/photos/0/0/men_main.gif; t=24b898086f91bda3580250bb65dca8918; societyguester=24b898086f91bda3580250bb65dca8918; id=965882188; xnsid=f71617dc; ver=7.0; loginfrom=nul'
url = "http://www.renren.com/965882188/profile"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Cookie": cookie_str
}


# 方式1: 在请求头中指定cookie信息
def meth1():
    resp = requests.get(url, headers=headers)
    body = resp.text
    print("46299" in body)


def meth2():
    # 方式2: 使用字典记录每一个cookie, 键:=前面的 值:=后的
    cookie_dic = {one_cookie.split("=")[0]: one_cookie.split("=")[1] for one_cookie in cookie_str.split("; ")}
    print(pprint.pformat(cookie_dic))

    resp = requests.get(url,
                            headers=headers,
                            cookies=cookie_dic,
                            )

    if resp.status_code == 200:
        body = resp.text
        print("46299" in body)


def meth3():
    # 1. 获取session对象
    session = requests.session()

    # 2. 使用session对象,进行登录,登录后seesion对象会记录用户相关的cookie信息
    login_url = "http://www.renren.com/PLogin.do"
    data = {
        "email": "15626046299",
        "password": "044610Fa"
    }

    response = session.post(login_url, data=data, headers=headers)
    # print(response.status_code)
    # print(response.content.decode())

    # 3. 再使用记录cookie信息对象session访问个人主页
    resp = session.get(url)
    if resp.status_code == 200:
        body = resp.text
        print("46299" in body)


if __name__ == "__main__":
    # meth1()

    # meth2()

    meth3()
