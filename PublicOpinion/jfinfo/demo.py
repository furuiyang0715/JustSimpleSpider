import re


def test_link():
    link = 'https://www.jfinfo.com/news/20161218/546317'
    _year = re.findall(r"news/(\d+)/", link)[0]
    print(_year)
    print(type(_year))


test_link()