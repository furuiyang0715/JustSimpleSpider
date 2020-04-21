import sys

import pymysql


def create_table():
    sql = '''
    CREATE TABLE IF NOT EXISTS `baidukeyword` (
      `KeyId` int(11) NOT NULL COMMENT '词条ID',
      `KeyWord` varchar(128) CHARACTER SET utf8 NOT NULL COMMENT '词条',
      UNIQUE KEY `KeyId` (`KeyId`),
      KEY `key_word` (`KeyWord`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='百度词条';
    '''


def csv_to_mysql(load_sql, host, port, user, password):
    '''
    This function load a csv file to MySQL table according to
    the load_sql statement.
    '''
    try:
        con = pymysql.connect(host=host,
                              user=user,
                              port=port,
                              password=password,
                              autocommit=True,
                              local_infile=1)
        print('Connected to DB: {}'.format(host))
        # Create cursor and execute Load SQL
        cursor = con.cursor()
        cursor.execute(load_sql)
        print('Succuessfully loaded the table from csv.')
        con.close()

    except Exception as e:
        print('Error: {}'.format(str(e)))
        sys.exit(1)


def main():
    # Execution Example
    csv_file = '/Users/furuiyang/gitzip/JustSimpleSpider/baidu/demo.csv'
    # csv_file = '/Users/furuiyang/gitzip/JustSimpleSpider/baidu/csv/csv_1_10000/key_words_1001_2000.csv'
    # csv_file = '/Users/furuiyang/gitzip/JustSimpleSpider/baidu/key_words_1_1000.csv'
    db = 'test_furuiyang'
    table = 'baidukeyword'
    load_sql = """
LOAD DATA LOCAL INFILE '{}' INTO TABLE {}.{} character set utf8 \
FIELDS TERMINATED BY ',' \
ENCLOSED BY '"' \
IGNORE 1 LINES;""".format(csv_file, db, table)

    print(load_sql)
    host = 'localhost'
    port = 3306
    user = ''
    password = ''
    csv_to_mysql(load_sql, host, port, user, password)


main()
