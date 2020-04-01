from hk_land.configs import TEST_MYSQL_HOST, TEST_MYSQL_PORT, TEST_MYSQL_USER, TEST_MYSQL_PASSWORD, TEST_MYSQL_DB
from hk_land.sql_pool import PyMysqlPoolBase


def contract_sql(to_insert: dict, table: str):
    ks = []
    vs = []
    for k in to_insert:
        ks.append(k)
        vs.append(to_insert.get(k))
    fields_str = "(" + ",".join(ks) + ")"
    values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
    base_sql = '''INSERT INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str + ''';'''
    return base_sql, tuple(vs)


def run():
    dd = {"id": 1,
          "name": "ruiyang",
          "age": '26',
          "mshu": "A developer.",
          "hobby": "sleep",
          }
    table = 'ruiyang_test'
    sql, vs = contract_sql(dd, table)
    '''
    REPLACE INTO `lgt_south_money_data` (Date,HKHFlow,HKHBalance,HKZFlow,HKZBalance,SouthMoney,Category) values (%s,%s,%s,%s,%s,%s,%s);
    (datetime.datetime(2020, 4, 1, 15, 22), Decimal('239313.53'), Decimal('3960686.47'), Decimal('102840.54'), Decimal('4097159.46'), Decimal('342154.07'), '南向资金')
    '''
    print(sql)
    print(vs)
    cfg = {
        "host": TEST_MYSQL_HOST,
        "port": TEST_MYSQL_PORT,
        "user": TEST_MYSQL_USER,
        "password": TEST_MYSQL_PASSWORD,
        "db": TEST_MYSQL_DB,
    }
    pool = PyMysqlPoolBase(**cfg)
    pool.delete('drop table ruiyang_test; ')
    create_sql = '''
    CREATE TABLE IF NOT EXISTS `{}` (
          `id` int AUTO_INCREMENT,
          `name` varchar(20) COMMENT '姓名',
          `age` int COMMENT '年龄',
          `hobby` varchar(40) COMMENT '爱好',
          `mshu` varchar(40)  COMMENT '描述',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_key` (`name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='关于我';
    '''.format("ruiyang_test")
    pool.insert(create_sql)
    # pool.dispose()

    count = pool.insert(sql, vs)
    print(count)
    pool.dispose()


run()
