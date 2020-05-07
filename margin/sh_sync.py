from margin.base import MarginBase


class ShSync(MarginBase):
    """上交融资融券标的"""
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'

    def load_juyuan(self):
        """将聚源已有的数据导入"""
        select_fields = ['SecuMarket', 'InnerCode', 'InDate', 'OutDate', 'TargetCategory', 'TargetFlag', 'ChangeReasonDesc',
                         # 'UpdateTime', 'JSID',
                         ]
        select_str = ",".join(select_fields).rstrip(",")
        # print(select_str)

        juyuan = self._init_pool(self.juyuan_cfg)
        sql = '''select {} from {};'''.format(select_str, self.juyuan_table_name)
        ret = juyuan.select_all(sql)
        # print(len(ret))
        # print(ret[10])
        return ret

    def _create_table(self):
        sql = '''
        
        
        '''


if __name__ == "__main__":
    ShSync().load_juyuan()