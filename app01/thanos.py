from django.utils.safestring import mark_safe

from thanos.service import crm
from app01 import models


class RoleConfig(crm.CrmConfig):
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return mark_safe('<input type="checkbox" name="obj_list" value="">')
        return mark_safe('<input type="checkbox" name="obj" value="%s">' % obj.id)

    def change(self, obj=None, is_header=False):
        if is_header:
            return '修改'
        return mark_safe('<a href="###">修改</a>')

    list_display = [checkbox, 'name', change]


############## 注册 ###############
crm.site.register(models.Role, RoleConfig)
crm.site.register(models.UserInfo)
