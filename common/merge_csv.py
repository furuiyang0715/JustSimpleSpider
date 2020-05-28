import traceback

import pandas as pd
import os


FolderPath = r'/Users/furuiyang/gitzip/JustSimpleSpider/Baidu/amerge_csv/11900001_12000000'
SaveFileName = r'key_words_11900001_12000000.data_dir'
SaveFilePath = r'/Users/furuiyang/gitzip/JustSimpleSpider/Baidu/amerge_csv'  # 拼接后要保存的文件路径
# 获取要合并的目标文件夹中的文件列表
file_list = os.listdir(FolderPath)
# 读取第一个 CSV 文件并包含表头
df = pd.read_csv(os.path.join(FolderPath, file_list[0]))
# 创建要保存的文件夹
os.makedirs(SaveFilePath, exist_ok=True)
# 将读取的第一个 CSV 文件写入合并后的文件保存
save_file = os.path.join(SaveFilePath, SaveFileName)
df.to_csv(save_file)
# 循环遍历列表中各个 CSV 文件名，并追加到合并后的文件
count = 0
try:
    for i in range(1, len(file_list)):
        print(os.path.join(FolderPath, file_list[i]))
        df = pd.read_csv(os.path.join(FolderPath, file_list[i]))
        count += df.shape[0]
        df.to_csv(save_file, encoding="utf-8", index=False, header=False, mode='a+')
except Exception:
    traceback.print_exc()
# 总数据量
print(count)
