from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from filter_tools.base_filter import BaseFilter

Base = declarative_base()


class Filter(Base):
    __tablename__ = "filter"  # 对应mysql中的表名
    id = Column(Integer, primary_key=True)
    hash_value = Column(String(40), index=True, unique=True)  # 索引且唯一


class MqlFilter(BaseFilter):
    """
    基于 mysql 的去重判断依据的存储
    """

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
        _filter = Filter(hash_value=hash_value)
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
        ret = session.query(Filter).filter_by(hash_value=hash_value).first()
        session.close()
        if ret is None:
            return False
        else:
            return True
