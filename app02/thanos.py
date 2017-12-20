from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django.shortcuts import render, redirect, reverse, HttpResponse

from thanos.service import crm
from app02 import models

crm.site.register(models.Role)
crm.site.register(models.Department)


class UserInfoConfig(crm.CrmConfig):

    def display_gender(self, obj=None, is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()

    def display_depart(self, obj=None, is_header=False):
        if is_header:
            return '部门'
        return 'abc'

    def display_roles(self, obj=None, is_header=False):
        if is_header:
            return '角色'
        return 'abc'

    list_display = ['id', 'name', 'email', display_gender, display_depart, display_roles]
    comb_filter = ['gender', 'depart', 'roles']


crm.site.register(models.UserInfo, UserInfoConfig)
