# 简单表示布隆过滤器的实现原理

# 计算布隆过滤器的长度
# 假如是我们使用了一个 256 M 的布隆过滤器
# 那么现在我们来计算这个过滤器的长度
import hashlib

length = 256 * 1024 * 1024 * 8
print(length)  # 2147483648
# 当我们对于某个值进行 md5 去特征值之后
m5 = hashlib.md5()
m5.update("ruiyang".encode())
feature = m5.hexdigest()
print(feature)  # f4f122f0d6344f425134f6b6521e1108
# 将这个特征值转换为十进制
num = int(feature, 16)
print(num)  # 325583683197404924561916843050611380488
# 将数值除以布隆过滤器的长度进行求余
ret = num % length
print(ret)  # 1377702152
# ret 即为该值在 布隆过滤器中的位置

