from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect, reverse, HttpResponse

from thanos.service import crm
from app01 import models


class RoleConfig(crm.CrmConfig):
    list_display = ['name']

    def delete(self, obj=None, is_header=False):
        print(self)
        print(obj)
        print(is_header)
        if is_header:
            return '删除123'
        return mark_safe('<a href="%s">删除123</a>' % self.get_delete_url(obj.id))

    def history_view(self):
        return HttpResponse('历史记录')

    def extra_urls(self):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name

        urlpatterns = [
            url(r'^history/$', self.history_view, name='%s_%s_history' % info),
        ]
        return urlpatterns


############## 注册 ###############
crm.site.register(models.Role, RoleConfig)
crm.site.register(models.UserInfo)
