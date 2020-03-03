# coding=utf8

from PublicOpinion.jfinfo.reference import Reference


class HKInfo(Reference):
    def __init__(self):
        super(HKInfo, self).__init__()
        self.index_url = 'http://www.jfinfo.com/reference/HK'
        self.more_url = 'http://www.jfinfo.com/articles_categories/more?page={}&category_id=83'
        self.max_page = 49


if __name__ == "__main__":
    runner = HKInfo()
    runner.start()
