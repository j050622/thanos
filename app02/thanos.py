from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django.shortcuts import render, redirect, reverse, HttpResponse

from thanos.service import admin
from app02 import models

admin.site.register(models.Role)
admin.site.register(models.Department)


class UserInfoConfig(admin.CrmConfig):
    show_add_btn = True

    show_search_form = True
    search_fields = ['username__contains', 'email__contains', 'gender']

    def display_gender(self, obj=None, is_header=False):
        """显示性别"""
        if is_header:
            return '性别'
        return obj.get_gender_display()

    def display_department(self, obj=None, is_header=False):
        """显示部门名称"""
        if is_header:
            return '部门'
        return obj.department.caption

    def display_roles(self, obj=None, is_header=False):
        """显示角色名"""
        if is_header:
            return '角色'
        text = []
        for role_obj in obj.roles.all():
            text.append(role_obj.name)

        return ','.join(text)

    list_display = ['id', 'username', 'email', display_gender, display_department, display_roles]

    comb_filter_rows = [admin.FilterRowOption('gender', is_choice=True),
                        admin.FilterRowOption('department'),
                        admin.FilterRowOption('roles', True)]


admin.site.register(models.UserInfo, UserInfoConfig)
