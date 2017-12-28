from . import models


class Contribute:
    """用户自动分配"""

    @classmethod
    def contribute(self):
        obj_list = models.ConsultantWeight.objects.all().order_by('-weight').values_list('consultant_id', 'cus_limit')
        print(obj_list)
