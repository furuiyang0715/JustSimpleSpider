import json
import sys
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests as re

from PublicOpinion.configs import SECRET, TOKEN


def get_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(TOKEN, timestamp, sign)
    return url


def ding_msg(msg):
    url = get_url()
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }

    message = {
        "msgtype": "text",
        "text": {
            "content": "{}@15626046299".format(msg)
        },
        "at": {
            "atMobiles": [
                "15626046299",
            ],
            "isAtAll": False
        }
    }

    message_json = json.dumps(message)
    resp = re.post(url=url, data=message_json, headers=header)
    if resp.status_code == 200:
        print("钉钉发送成功: {}".format(msg))
    else:
        print("钉钉消息发送失败 ")


def demo():
    try:
        "999" / 100
    except:
        exc_type, exc_value, exc_traceback_obj = sys.exc_info()
        error_info = {
            'msg': "程序运行出错",
            'exc_type': exc_type,
            'exc_value': exc_value,
        }
        ding_msg(error_info)


if __name__ == "__main__":
    demo()

    pass
