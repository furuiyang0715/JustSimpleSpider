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


if __name__ == "__main__":

    my_add(1, 2)

    my_add_1(1000, 1000)
