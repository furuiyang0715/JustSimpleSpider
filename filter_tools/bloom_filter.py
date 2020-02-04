# 基于 redis 的布隆过滤器的实现

# （1） 多个 hash 函数的实现和求值
# （2） hash 表的实现以及实现对应的映射以及判断

import hashlib


class MultipleHash(object):
    def __init__(self, salts, hash_func_name='md5'):
        """
        该类实现对某个数值进行加盐hash的过程
        :param salts: 对原始的数据进行预定义加盐
        :param hash_func_name: 可使用多个 hash 函数
        """
        self.hash_func = getattr(hashlib, hash_func_name)
        if len(salts) < 3:
            raise Exception("请至少输入 3 个 salts")
        self.salts = salts

    def _safe_data(self, data):
        """
        对即将hash的数据进行预处理
        这里我已经确认我运行在 py3 环境中
        就不像之前一样对系统进行判断
        :param data:
        :return:
        """
        if isinstance(data, str):
            return data.encode()
        elif isinstance(data, bytes):
            return data
        else:
            raise Exception("被hash值必须是一个字符串")

    def get_hash_value(self, data):
        """
        根据提供的数据 返回多个hash函数值
        :param data:
        :return:
        """
        hash_values = []
        for i in self.salts:
            hash_obj = self.hash_func()
            hash_obj.update(self._safe_data(data))
            hash_obj.update(self._safe_data(i))
            ret = hash_obj.hexdigest()
            # 将结果的 16 进制字节转换为 10 进制
            hash_values.append(int(ret, 16))
        return hash_values


if __name__ == "__main__":
    h = MultipleHash(salts=['1', '2', '3'])
    print(h.get_hash_value("ruiyang"))
