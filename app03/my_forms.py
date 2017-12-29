from django.forms import ModelForm, Form, fields
from django.forms import widgets as wgs
from . import models


class LoginForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['username', 'password']

        error_messages = {
            "username": {"required": '用户名不能为空'},
            "password": {"required": '密码不能为空'},
        }
