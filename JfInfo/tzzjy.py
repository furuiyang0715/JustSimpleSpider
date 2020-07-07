# coding=utf8

from JfInfo.reference import Reference


class TZZJY(Reference):
    def __init__(self):
        super(TZZJY, self).__init__()
        self.index_url = 'http://www.jfinfo.com/reference/tzzjy'
        self.more_url = 'http://www.jfinfo.com/articles_categories/more?page={}&category_id=59'
        self.max_page = 20
        self.name = '投资者教育'


if __name__ == "__main__":
    runner = TZZJY()
    runner.start()
