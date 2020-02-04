from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from filter_tools.base_filter import BaseFilter

Base = declarative_base()


# class Filter(Base):
#     __tablename__ = "filter"  # 对应mysql中的表名
#     id = Column(Integer, primary_key=True)
#     hash_value = Column(String(40), index=True, unique=True)  # 索引且唯一


class MqlFilter(BaseFilter):
    """
    基于 mysql 的去重判断依据的存储
    """
    def __init__(self, *args, **kwargs):

        # 因为不用项目的去重依据应该存储在不同的表中 所以我们需要为数据库动态创建

        # 动态创建类的两种办法
        # (1) 一种是直接将类写在初始化方法中
        # (2) 另外一种是使用 type 动态创建
        # class Filter(Base):
        #     # __tablename__ = "filter"  # 对应mysql中的表名
        #     __tablename__ = kwargs.get("mysql_table_name")
        #     id = Column(Integer, primary_key=True)
        #     hash_value = Column(String(40), index=True, unique=True)  # 索引且唯一
        # self.table = Filter

        self.table = type(
            kwargs.get("mysql_table_name"),
            (Base, ),
            dict(
                __tablename__=kwargs.get("mysql_table_name"),
                id=Column(Integer, primary_key=True),
                hash_value=Column(String(40), index=True, unique=True),
            )
        )
        BaseFilter.__init__(self, *args, **kwargs)

    def _get_storage(self):
        """
        返回一个 mysql 的连接对象 （在此处为 sqlalchemy 的连接对象）
        :return:
        """
        engine = create_engine(self.mysql_url)
        Base.metadata.create_all(engine)    # 创建表 如果已有就忽略
        session = sessionmaker(engine)
        return session

    def _save(self, hash_value):
        """
        利用 mysql 数据库进行存储
        :param hash_value:
        :return:
        """
        session = self.storage()
        _filter = self.table(hash_value=hash_value)
        session.add(_filter)
        session.commit()
        session.close()

    def _is_exist(self, hash_value):
        """
        判断 mysql 数据库中是否有对应的判断依据
        :param hash_value:
        :return:
        """
        session = self.storage()
        ret = session.query(self.table).filter_by(hash_value=hash_value).first()
        session.close()
        if ret is None:
            return False
        else:
            return True


if __name__ == "__main__":
    f = MqlFilter(
        mysql_url="mysql+pymysql://root:password@localhost:3306/db_name?charset=utf8",
        mysql_table_name="test_filter"
                  )

    datas = ['ruiyang', 'Ruiyang', '33', 'pwd', "11", "22", "33", "ruiyang"]
    for d in datas:
        if f.is_exist(d):
            print("{} 数据已经存在".format(d))
            # print(f.storage)
        else:
            f.save(d)
            print("添加数据 {}".format(d))
