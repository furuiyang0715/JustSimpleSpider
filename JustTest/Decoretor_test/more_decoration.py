def deco1(func):
    def wrapper(*args, **kwargs):
        print('before test1 ...')
        func(*args, **kwargs)
        print('after test1 ...')
    return wrapper  # 返回内层函数的引用


def deco2(func):
    def wrapper(*args, **kwargs):
        print('before test2 ...')
        func(*args, **kwargs)
        print('after test2 ...')
    return wrapper  # 返回内层函数的引用


# @deco2
# @deco1
# def add(a, b):
#     print(a+b)


def add(a, b):
    print(a+b)


if __name__ == "__main__":
    print("开始")
    add = deco1(add)
    print("第一层包装结束")
    add = deco2(add)
    print('第二层包装结束')
    add(1, 2)
    print("执行结束")
