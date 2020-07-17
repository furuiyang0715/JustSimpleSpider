import sys
import time
import traceback
from collections import deque

# # 创建空的队列
# d1 = deque()
# print(d1)   # deque([])

# # 创建已经存在元素的对象:从 iterable （迭代对象) 数据创建。如果 iterable 没有指定，新队列为空。
# d = deque("pig")
# print(d)    # deque(['p', 'i', 'g'])

# # 创建指定最大长度的队列
# d = deque(maxlen=10)
# for i in range(1, 101):
#     try:
#         d.append(i)
#         # print(d)
#     except:
#         traceback.print_exc()
#         break
#
# print(d)
# # deque([91, 92, 93, 94, 95, 96, 97, 98, 99, 100], maxlen=10)

# # 从最右边添加元素
# d = deque()
# d.append({"what": "apple"})
# print(d)

# # 从左边添加元素
# d = deque()
# for i in (1, 2, 3):
#     d.appendleft(i)
# print(d)


# # 创建一份浅拷贝
# d = deque([[1, 2, 3], "apple", 'ruiyang'])
# dd = d.copy()
# print(id(d))   # 4383179616
# print(id(dd))  # 4383831440
# d[0].append(4)
# print(d)  # deque([[1, 2, 3, 4], 'apple', 'ruiyang'])
# print(dd)  # deque([[1, 2, 3, 4], 'apple', 'ruiyang'])

# # 计算队列中等于某个值的个数
# d = deque([[1, 2, 3], "apple", 'ruiyang', 'apple'])
# print(d.count("apple"))

# # extend(iterable) 扩展deque的右侧，通过添加iterable参数中的元素。
# d = deque("ruiyang")
# d.extend(["a", "b", "c"])
# print(d)
#
# # extendleft(iterable)
# # 扩展deque的左侧，通过添加iterable参数中的元素。注意，左添加时，在结果中iterable参数中的顺序将被反过来添加。
# d.extendleft(['e', 'f', 'g'])
# print(d)
# sys.exit(0)

# # insert(i, x): 在位置 i 插入 x 。如果插入会导致一个限长 deque 超出长度 maxlen 的话，就引发一个 IndexError
# d9 = deque("1234567890", maxlen=11)
# d9.insert(0, {"index": 100})
# print(d9)
# # Deque的最大尺寸，如果没有限定的话就是 None 。
# print(d9.maxlen)
# print(len(d9))
# try:
#     d9.insert(0, "666")
# except IndexError:
#     print("长度超出")


# # pop() 移去并且返回一个元素，deque 最右侧的那一个。 如果没有元素的话，就引发一个 IndexError
# d = deque("ruiyang")
# while True:
#     try:
#         print(d.pop())
#     except:
#         traceback.print_exc()
#         break
#     time.sleep(1)

# # popleft() 移去并且返回一个元素，deque 最左侧的那一个。 如果没有元素的话，就引发 IndexError。
# d = deque("ruiyang")
# while True:
#     try:
#         print(d.popleft())
#     except:
#         traceback.print_exc()
#         break
#     time.sleep(1)
#
# sys.exit(0)

# # remove(value) 移除找到的第一个 value。 如果没有的话就引发 ValueError。
# d = deque("ruiyang")
# d.remove('g')
# print(d)
#
# try:
#     d.remove("o")
# except:
#     traceback.print_exc()


# # reverse() 将deque逆序排列。返回 None 。
# d = deque("ruiyang")
# print("***** ", d)
# d.reverse()
# print("##### ", d)
#
# sys.exit(0)

# # rotate(n=1) 向右循环移动 n 步。 如果 n 是负数，就向左循环。
# # 如果deque不是空的，向右循环移动一步就等价于 d.appendleft(d.pop()) ， 向左循环一步就等价于 d.append(d.popleft()) 。
# d = deque("ruiyang")
# print(">>>1", d)
# d.rotate(1)
# print(">>>2", d)


# 移除全部的元素 使其长度为 0
d = deque("ruiyang")
print(d)
d.clear()
print(d)

'''
除了以上操作，deque 还支持迭代、封存、len(d)、reversed(d)、copy.copy(d)、copy.deepcopy(d)、
成员检测运算符 in 以及下标引用例如通过 d[0] 访问首个元素等。 索引访问在两端的复杂度均为 O(1) 但在中间则会低至 O(n)。 
如需快速随机访问，请改用列表。

'''

d = deque("ruiyang")
print(len(d))

for one in d:
    print(one)

for one in reversed(d):
    print(one)

import copy
d.appendleft([1, 2, 3])
d1 = copy.deepcopy(d)
d[0].append(4)
print(d)
print(d1)

print("r" in d)
