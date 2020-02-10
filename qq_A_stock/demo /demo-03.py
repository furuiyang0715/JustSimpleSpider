# 测试生成 token
import pprint
import time
import base64
import hmac

import requests as re


# ret = re.get("https://new.qq.com/ch2/Agu")
# print(ret)
# # print(dir(ret))
# cookies = dict(ret.cookies)
# print(pprint.pformat(cookies))
# # print(dir(cookies))  # {}

# 主要是不知这个token是否是始终不变的
# 8f6b50e1667f130c10f981309e1d8200
# 2a92b3959fcb4b2f8cf6a7eb68c55ec3

import os
import uuid
ret = uuid.uuid4().hex
print(ret)



# def generate_token(key, expire=3600):
#     '''
#     @Args:
#         key: str (用户给定的key，需要用户保存以便之后验证 token,每次产生token 时的 key 都可以是同一个key)
#         expire: int(最大有效时间，单位为s)
#     @Return:
#         state: str
#     '''
#     ts_str = str(time.time() + expire)
#     ts_byte = ts_str.encode("utf-8")
#     sha1_tshexstr = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
#     token = ts_str+':'+sha1_tshexstr
#     b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
#     return b64_token.decode("utf-8")
#
#
# ret = generate_token("瑞阳")
# print(ret)


