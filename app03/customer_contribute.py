from . import models


class Contribute:
    """用户自动分配"""
    consultants = []
    iter_consultant = []
    roll_back_id_list = []

    @classmethod
    def get_contribution(cls):
        """获取权限分配表"""

        obj_list = models.ConsultantWeight.objects.all().order_by('-weight').values_list('consultant_id', 'cus_limit')
        max_num = models.ConsultantWeight.objects.values_list('cus_limit').all().order_by('-cus_limit')[0][0]
        consultant_lst = []
        for n in range(1, max_num + 1):
            for sub_lst in obj_list:
                if sub_lst[1] >= n:
                    consultant_lst.append(sub_lst[0])
        cls.consultants = consultant_lst

    @classmethod
    def get_consultant_id(cls):
        if not cls.consultants:
            cls.get_contribution()

        if not cls.iter_consultant:
            cls.iter_consultant = iter(cls.consultants)

        try:
            consultant_id = next(cls.iter_consultant)
        except StopIteration:
            cls.iter_consultant = iter(cls.consultants)
            consultant_id = 2  ##### 这里有待修改，重新对上面的consultant_lst进行遍历

        return consultant_id

    @classmethod
    def rollback(cls):
        pass
