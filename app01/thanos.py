from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect, reverse, HttpResponse

from thanos.service import crm
from app01 import models


###自定义类
class RoleConfig(crm.CrmConfig):
    list_display = ['id', 'name']

    def get_show_add_btn(self):
        if ('session里获取权限，有权限，执行下面的代码'):
            self.show_add_btn = True
        return self.show_add_btn

    def history_view(self):
        return HttpResponse('历史记录')

    def extra_urls(self):
        info = self.model_class._meta.app_label, self.model_class._meta.model_name
        urlpatterns = [
            url(r'^history/$', self.history_view, name='%s_%s_history' % info),
        ]
        return urlpatterns


class UserInfoConfig(crm.CrmConfig):
    list_display = ['username']
    show_add_btn = True


############## 注册 ###############
crm.site.register(models.Role, RoleConfig)
crm.site.register(models.UserInfo, UserInfoConfig)
