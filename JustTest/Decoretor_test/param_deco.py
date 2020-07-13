def auth(permission):
    # 这里的 permission 相当于装饰器的参数
    def _auth(func):
        def wrapper(*args, **kwargs):
            print(f"验证权限[{permission}]...")
            func(*args, **kwargs)
            print("执行完毕...")
        return wrapper
    return _auth


@auth("add")
def add(a, b):
    """
    求和运算
    """
    print(a + b)


if __name__ == "__main__":
    # 传参装饰器的执行
    add(1, 2)
