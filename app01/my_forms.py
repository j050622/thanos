"""
自定义Form类
"""

from django.forms import ModelForm, Form
from . import models


class UserInfoForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = '__all__'

        error_messages = {
            "username": {"required": '用户名不能为空'}
        }
