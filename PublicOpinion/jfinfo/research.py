# coding=utf8

from PublicOpinion.jfinfo.reference import Reference


class Research(Reference):
    def __init__(self):
        super(Research, self).__init__()
        self.index_url = 'http://www.jfinfo.com/research'
        self.more_url = 'http://www.jfinfo.com/articles_categories/more?page={}&category_id=23'
        self.max_page = 185


if __name__ == "__main__":
    runner = Research()
    runner.start()
