from django.forms import ModelForm
from django.forms import widgets as wgs
from rbac import models


class LoginForm(ModelForm):
    class Meta:
        model = models.User
        fields = ['username', 'password']

        error_messages = {
            "username": {"required": '用户名不能为空'},
            "password": {"required": '密码不能为空'},
        }
        widgets = {
            "password": wgs.PasswordInput,
        }
