from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django.shortcuts import render, redirect, reverse, HttpResponse

from thanos.service import crm
from app02 import models

crm.site.register(models.Role)
crm.site.register(models.Department)


class UserInfoConfig(crm.CrmConfig):
    show_add_btn = True
    show_actions = True

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

    comb_filter_rows = [crm.FilterRowOption('gender'),
                        crm.FilterRowOption('department'),
                        crm.FilterRowOption('roles', True)]


crm.site.register(models.UserInfo, UserInfoConfig)
