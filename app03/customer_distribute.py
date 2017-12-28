from . import models


class Distribute:
    """用户自动分配"""
    consultants = None
    iter_consultant = None
    rollback_id_list = None

    @classmethod
    def get_distribution(cls):
        """获取权限分配表"""
        obj_list = models.ConsultantWeight.objects.all().order_by('-weight').values_list('consultant_id', 'cus_limit')
        tmp_list = []

        # 原始版本
        # max_num = models.ConsultantWeight.objects.values_list('cus_limit').all().order_by('-cus_limit')[0][0]
        # for n in range(1, max_num + 1):
        #     for sub_lst in obj_list:
        #         if sub_lst[1] >= n:
        #             tmp_list.append(sub_lst[0])

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
        if not cls.consultants:
            cls.get_distribution()
        if not cls.iter_consultant:
            cls.iter_consultant = iter(cls.consultants)

        try:
            if cls.rollback_id_list:
                # 如果有回滚id，直接返回
                return cls.rollback_id_list.pop(0)
            consultant_id = next(cls.iter_consultant)
        except StopIteration:
            cls.iter_consultant = iter(cls.consultants)
            consultant_id = 2  ###########待修改

        return consultant_id

    @classmethod
    def rollback(cls, cid):
        """如果数据库回滚触发，把触发时的顾问id添加到回滚id列表"""
        cls.rollback_id_list.append(cid)
