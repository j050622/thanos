import datetime
from urllib.request import quote

from django.conf.urls import url
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import JsonResponse, StreamingHttpResponse
from django.utils.safestring import mark_safe
from django.db.transaction import atomic
from django.forms import Form, fields, widgets
from django.db.models import Q

from thanos.service import crm
from . import models


class MenuConfig(crm.CrmConfig):
    pass


class PermissionGroupConfig(crm.CrmConfig):
    list_display = ['title']
    list_editable = ['title']


class PermissionConfig(crm.CrmConfig):
    def display_group(self, obj=None, is_header=False):
        if is_header:
            return '权限组'
        return obj.group.title

    def display_menu_ref(self, obj=None, is_header=False):
        if is_header:
            return '菜单URL'
        menu_ref = obj.menu_ref
        if not menu_ref:
            return '--'
        else:
            return obj.menu_ref.title

    list_display = ['title', 'url', 'code', display_menu_ref, display_group]
    list_editable = ['title']
    list_per_page = 100


class RoleConfig(crm.CrmConfig):
    pass


class UserConfig(crm.CrmConfig):
    pass
