# 测试 simhash 库的简单使用
# pip install simhash

import re
from simhash import Simhash


def get_features(s):
    """
    对文本全部转小写 去掉空白字符以及标点符号
    :param s:
    :return:
    """
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


# 计算出这几个文本的 simhash 值
print('%x' % Simhash(get_features('How are you? I am fine. Thanks.')).value)
print('%x' % Simhash(get_features('How are u? I am fine.     Thanks.')).value)
print('%x' % Simhash(get_features('How r you?I    am fine. Thanks.')).value)