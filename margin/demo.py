# https://www.jianshu.com/p/cea4c8f67cd6

import xlrd

# 打开已有的工作薄
wb = xlrd.open_workbook('20200506.xls')

# 获取所有的sheet名称
sheet_names = wb.sheet_names()
print(sheet_names)

# 获得sheet对象
# 汇总信息
# ws = wb.sheet_by_index(0)
# ws = wb.sheet_by_name('汇总信息')
# 获取sheet对象的属性：表名、总行数、总列数
# print(ws.name, ws.nrows, ws.ncols)

# 明细信息
detail = wb.sheet_by_name("明细信息")
print(detail.name, detail.nrows, detail.ncols)


# 获得某一行或某一列数据，返回list
head = detail.row_values(0)
print(head)
row_4 = detail.row_values(3)
print(row_4)
# cloumn_5 = detail.col_values(4)
# print(cloumn_5)
# Row_4 = detail.row(3)  # 此方法list中包含单元格类型
# print(Row_4)
# Column_5 = detail.col(4)  # 此方法list中包含单元格类型


# # 获得某一单元格的值
# cell_1_1 = detail.cell_value(0, 0)
# cell_1_1 = detail.cell(0, 0).value
# cell_1_1 = detail.row_values(0)[0]
# cell_1_1 = detail.col_values(0)[0]
# cell_1_1 = detail.row(0)[0].value
# cell_1_1 = detail.col(0)[0].value