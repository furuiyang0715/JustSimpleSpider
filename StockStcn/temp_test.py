lst = ['apple', 'ai', 'bee', 'fu', 'ruiyang']


def che(i: str):
    if i.startswith('a'):
        return True
    else:
        return False


lst = [i for i in lst if che(i)]

print(lst)