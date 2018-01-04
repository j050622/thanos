"""
configs中的Config类在继承CrmConfig之前，可以从本模块继承一些类，用于自定义权限，将粒度
控制到按钮
"""
from thanos.service import crm
from CRM import settings


class BasePermission(crm.CrmConfig):
    """
    判断是否显示添加、编辑、删除等按钮
    """

    def get_show_add_btn(self):
        """判断是否显示添加按钮"""

        codes_list = self.request.session.get(settings.PERM_CODES_LIST)
        if 'add' not in codes_list:
            return False
        return self.show_add_btn

    def get_list_editable(self):
        """判断是否可以进行编辑"""

        codes_list = self.request.session.get(settings.PERM_CODES_LIST)
        if 'change' not in codes_list:
            return []
        result = []
        if self.list_editable:
            result.extend(self.list_editable)
        return result

    def get_list_display(self):
        """判断是否显示删除按钮"""

        codes_list = self.request.session.get(settings.PERM_CODES_LIST)
        result = []
        if self.list_display:
            result.extend(self.list_display)

            result.insert(0, crm.CrmConfig.checkbox)
            if 'delete' in codes_list:
                result.append(crm.CrmConfig.ele_delete)

        return result
