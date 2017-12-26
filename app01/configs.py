"""
在crm中注册表时的自定义配置项
"""

import json

from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import JsonResponse

from thanos.service import crm
from . import models
from .forms import UserInfoForm


class RoleConfig(crm.CrmConfig):
    list_display = ['name']
    show_search_form = True
    search_fields = ['name__contains']

    def get_show_add_btn(self):
        """通过session中设置的权限来控制是否显示添加记录按钮"""
        if (1):
            self.show_add_btn = True
        return self.show_add_btn

    def history_view(self):
        """模拟自定义扩展URL的视图函数"""
        return HttpResponse('历史记录')

    def extra_urls(self):
        """模拟自定义扩展URL"""
        info = self.model_class._meta.app_label, self.model_class._meta.model_name
        urlpatterns = [
            url(r'^history/$', self.history_view, name='%s_%s_history' % info),
        ]
        return urlpatterns


class UserInfoConfig(crm.CrmConfig):
    list_display = ['username', 'email']
    list_editable = ['username']

    def get_list_display(self):
        result = []
        if self.list_display:
            result.extend(self.list_display)
            result.insert(0, crm.CrmConfig.checkbox)
            result.append(crm.CrmConfig.ele_delete)
        return result

    show_add_btn = True
    model_form_class = UserInfoForm
    show_actions = True
    show_search_form = True
    search_fields = ['username__contains', 'email__contains']

    def multi_init(self, request):
        """批量初始化"""
        pk_list = request.POST.getlist('pk')
        print('模拟执行初始化函数')

    multi_init.short_desc = '批量初始化'

    def multi_del(self, request):
        """批量删除"""
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()

    multi_del.short_desc = '批量删除'

    ### 自定义action函数 ###
    actions = [multi_init, multi_del]
