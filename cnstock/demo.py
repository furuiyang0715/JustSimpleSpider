def get_list():
    for i in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
        for j in i:
            if j == 6:
                return
            yield j


ret = get_list()


for r in ret:
    print(r)