import time


def my_add(a, b):
    """简单函数"""
    print(a + b)


def my_add_1(l1, l2):
    """计算函数运行时间"""
    t1 = time.time()
    for a in range(l1):
        for b in range(l2):
            a + b
    t2 = time.time()
    print(t2 - t1)


# def timer(func, *args):
#     """将函数作为参数传入去计算执行时间
#     【高阶函数】
#     """
#     start = time.time()
#     func(*args)
#     time.sleep(2)  # 模拟耗时操作
#     long = time.time() - start
#     print(f'共耗时{long}秒。')


def timer(func):

    def wrapper(*args, **kwargs):
        """被装饰的过程"""
        start = time.time()
        func(*args, **kwargs)  # 此处拿到了被装饰的函数func
        time.sleep(2)  # 模拟耗时操作
        long = time.time() - start
        print(f'共耗时{long}秒。')

    return wrapper  # 返回内层函数的引用


def main():

    # my_add(1, 2)
    #
    # my_add_1(1000, 1000)
    #
    # timer(my_add, 1000, 2000)

    @timer
    def add(a, b):
        print(a + b)

    # add = timer(add)  # 此处返回的是timer.<locals>.wrapper函数引用

    add(1, 2)  # 正常调用add

    '''
    ->> 模块加载 
    ->> 遇到@，执行timer函数，传入add函数 
    ->> 生成timer.<locals>.wrapper函数并命名为add，其实是覆盖了原同名函数 
    ->> 调用add(1, 2) 
    ->> 去执行timer.<locals>.wrapper(1, 2) 
    ->> wrapper内部持有原add函数引用(func)，调用func(1, 2) 
    ->>继续执行完wrapper函数
    '''
    pass


if __name__ == "__main__":
    main()
