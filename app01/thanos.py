from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django.shortcuts import render, redirect, reverse, HttpResponse

from thanos.service import crm
from app01 import models


class UserInfoForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = '__all__'

        error_messages = {
            "username": {"required": '用户名不能为空'}
        }


###自定义类
class RoleConfig(crm.CrmConfig):
    list_display = ['name']
    show_search_form = True
    search_fields = ['name__contains']

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
    list_display = ['username', 'email']
    show_add_btn = True
    model_form_class = UserInfoForm

    show_search_form = True
    # search_fields = ['username__contains', 'email__contains', 'id__contains']
    search_fields = ['username__contains', 'email__contains', 'id__contains', 'id__gt']


############## 注册 ###############
crm.site.register(models.Role, RoleConfig)
crm.site.register(models.UserInfo, UserInfoConfig)
