# def add(a, b):
#     """
#     返回两数 a b 之和
#     :param a:
#     :param b:
#     :return:
#     """
#     return a + b
#
#
# if __name__ == "__main__":
#     print("origin")
#     print(add)
#     print(add.__name__)
#     print(add.__doc__)

import functools


def auth1(permission):
    # 这里的 permission 相当于装饰器的参数
    def _auth(func):
        def wrapper(*args, **kwargs):
            print(f"验证权限[{permission}]...")
            func(*args, **kwargs)
            print("执行完毕...")
        return wrapper
    return _auth


def auth(permission):
    def _auth(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"验证权限[{permission}]...")
            func(*args, **kwargs)
            print("执行完毕...")

        return wrapper

    return _auth


@auth("add")
# @auth1("add")
def add(a, b):
    """
    返回两数 a b 之和
    :param a:
    :param b:
    :return:
    """
    return a + b


if __name__ == "__main__":
    """
    functools.wraps内部通过partial和update_wrapper对函数进行再加工，
    将原始被装饰函数(add)的属性拷贝给装饰器函数(wrapper)。
    """
    print("wrapped")
    print(add)
    print(add.__name__)
    print(add.__doc__)
