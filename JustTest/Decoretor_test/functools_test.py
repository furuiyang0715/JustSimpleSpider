# https://zhuanlan.zhihu.com/p/45535784

import functools


def add(a, b):
    print(a + b)


if __name__ == "__main__":
    # partial用于部分应用一个函数，它基于一个函数创建一个可调用对象，把原函数的某些参数固定，调用时只需要传递未固定的参数即可。
    add = functools.partial(add, 1)
    add(2)
