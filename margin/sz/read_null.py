'''读取内容为空的下载文件'''

import xlrd

file = '/Users/furuiyang/gitzip/JustSimpleSpider/margin/sz/data_dir/2020-05-10.xlsx'


def read_xlrd(file):
    wb = xlrd.open_workbook(file)
    sheet_names = wb.sheet_names()  # ['融资融券标的证券信息']
    ws = wb.sheet_by_name('融资融券标的证券信息')

    if ws.nrows < 10:
        print("当日无数据")
        return

    # 获取sheet对象的属性：表名、总行数、总列数
    # print(ws.name, ws.nrows, ws.ncols)

    head = ws.row_values(0)
    # ['证券代码', '证券简称', '融资标的', '融券标的', '当日可融资', '当日可融券', '融券卖出价格限制']

    for i in range(1, ws.nrows):
        print(i, ">>> ", ws.row_values(i))


if __name__ == "__main__":

    read_xlrd(file)
