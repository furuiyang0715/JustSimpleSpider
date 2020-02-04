"""以一种更加通用的模式去运用海明距离"""

import re
from simhash import Simhash, SimhashIndex


def get_features(s):
    """
    对文本进行预处理
    转小写；去除空白字符以及标点符号
    :param s:
    :return:
    """
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


# 我们已经存在的数据
data = {
    1: u'How are you? I Am fine. blar blar blar blar blar Thanks.',
    2: u'How are you i am fine. blar blar blar blar blar than',
    3: u'This is simhash test.',
}
# 由初始数据建立的 key 以及 simhash 值的对象集
objs = [(str(k), Simhash(get_features(v))) for k, v in data.items()]
# 建立索引 可索引到的相似度海明距离是 3
index = SimhashIndex(objs, k=3)
print(index.bucket_size())  # 11
# 计算一个新来数据的 simhash 值
s1 = Simhash(get_features(u'How are you i am fine. blar blar blar blar blar thank'))
# 找到数据库中与此最接近的一个 simhash 值的索引
print(index.get_near_dups(s1))
# 将新数据添加到原有的索引中
index.add('4', s1)
print(index.get_near_dups(s1))

"""
如果我们要在实际项目上使用 simhash 计算，很显然需要保存这个索引对象 
因此我们可以考虑使用 序列化工具。

序列化工具： 将一个对象转换为二进制的一个数据。
反序列化工具： 将二进制恢复为一个对象。

"""