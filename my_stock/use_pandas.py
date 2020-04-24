import pandas as pd


# pandas 官方文档: https://pandas.pydata.org/docs/getting_started/index.html#getting-started

# 读取 ppcsv 文件
file = "buy.csv"
datas = pd.read_csv(file, encoding='utf-8')
print(datas)

# 将 df 数据转换为字典列表 每行为一个数据
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_dict.html
df = pd.DataFrame({'col1': [1, 2],
                   'col2': [0.5, 0.75]},
                  index=['row1', 'row2'])
data = df.to_dict("records")
print(df)
print(data)
