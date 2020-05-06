from margin.base import MarginBase


class ShSync(MarginBase):
    """上交融资融券标的"""
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'

    def load_juyuan(self):
        """将聚源已有的数据导入"""

        juyuan = self._init_pool(self.juyuan_cfg)
        sql = '''select * from {} limit 10;'''.format(self.juyuan_table_name)
        ret = juyuan.select_all(sql)
        print(ret)


if __name__ == "__main__":
    ShSync().load_juyuan()