from filter_tools.base_filter import BaseFilter


class MemoryFilter(BaseFilter):
    """
    基于 python 中的 set 结构进行去重判断依据的存储
    """

    def _get_storage(self):
        return set()

    def _save(self, hash_value):
        """
        利用 set 进行存储
        :param hash_value:
        :return:
        """
        self.storage.add(hash_value)  # 向 set 中添加数据

    def _is_exist(self, hash_value):
        if hash_value in self.storage:
            return True
        else:
            return False
