import re

ret = int('7,539,008'.replace(',', ''))
ret2 = re.findall("-?[\d\.]+", '7,539,008')
print(ret2)



import re
import time

a = "7,539,008"

start = time.time()

for i in range(1000000):
    # b = int("".join(re.findall("-?[\d\.]+",a)))
    b = int(a.replace(',', ''))
    # b = int("".join(a.split(",")))



end = time.time()


print("执行100万次完成时间:", end - start)

# 执行100万次完成时间: 2.009002685546875  方式 :    int("".join(re.findall("-?[\d\.]+",a)))    re
# 执行100万次完成时间: 0.6676313877105713  方式 :   int('7,539,008'.replace(',', ''))
#  执行100万次完成时间: 0.5756700038909912  方式 :  int("".join(a.split(",")))



