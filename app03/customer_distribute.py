from . import models


class Distribute:
    """用户自动分配"""
    consultants = None
    iter_consultants = None
    reset_status = False
    rollback_id_list = None

    @classmethod
    def get_distribution(cls):
        """获取权限分配表"""
        obj_list = models.ConsultantWeight.objects.all().order_by('-weight').values_list('consultant_id', 'cus_limit')
        tmp_list = []

        n = 0
        while 1:
            flag = False
            for sub_lst in obj_list:
                if sub_lst[1] > n:
                    tmp_list.append(sub_lst[0])
                    flag = True
            n += 1
            if not flag:
                break

        cls.consultants = tmp_list

    @classmethod
    def get_consultant_id(cls):
        """从迭代器中获取当前要被分配客户的课程顾问的id"""
        if not cls.consultants:
            cls.get_distribution()
        if not cls.consultants:
            # 没有课程顾问
            return None
        if not cls.iter_consultants:
            cls.iter_consultants = iter(cls.consultants)

        try:
            if cls.rollback_id_list:
                # 如果有回滚id，直接返回
                return cls.rollback_id_list.pop(0)
            consultant_id = next(cls.iter_consultants)
        except StopIteration:
            if cls.reset_status:
                cls.get_distribution()
                cls.reset_status = False

            cls.iter_consultants = iter(cls.consultants)
            consultant_id = cls.get_consultant_id()

        return consultant_id

    @classmethod
    def reset(cls):
        cls.reset_status = True

    @classmethod
    def rollback(cls, cid):
        """如果数据库回滚触发，把触发时的顾问id添加到回滚id列表"""
        cls.rollback_id_list.append(cid)
