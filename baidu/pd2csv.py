import os

import pandas as pd
from sqlalchemy import create_engine

from baidu.configs import MYSQL_PASSWORD

csv_dir = '/Users/furuiyang/gitzip/JustSimpleSpider/baidu/final_csv_dir'


def listfiles(ldir: str, r: bool = True):
    lst = []
    csv_dirs = os.listdir(ldir)
    for one in csv_dirs:
        one = os.path.join(ldir, one)
        if os.path.isdir(one):
            if r:
                lst.extend(listfiles(one))
            else:
                pass
        else:
            lst.append(one)
    return lst


def load2sql(file):
    try:
        data = pd.read_csv(file, encoding='utf-8')
        engine = create_engine('mysql+pymysql://rootb:{}@14.152.49.155:8998/test_furuiyang?charset=utf8'.format(MYSQL_PASSWORD))
        '''
        CREATE TABLE IF NOT EXISTS `baidukeyword` (
          `KeyId` int(11) NOT NULL COMMENT '词条ID',
          `KeyWord` varchar(128) CHARACTER SET utf8 NOT NULL COMMENT '词条',
          UNIQUE KEY `KeyId` (`KeyId`),
          KEY `key_word` (`KeyWord`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='百度词条';
        '''
        data.to_sql('baidukeyword',
                    index=False,
                    con=engine,
                    if_exists='append',
                    )
    except Exception as e:
        print(e)


def main():
    lst = listfiles(csv_dir)
    for file in lst:
        print(file)
        load2sql(file)
        print()


main()
