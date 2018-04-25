from django.shortcuts import render, redirect, reverse

from . import my_forms
from rbac import models as rbac_models
from rbac.service.init_permission import init_permission


def login(request):
    """登录"""

    if request.method == 'GET':
        login_form = my_forms.LoginForm
        return render(request, 'login.html', {"login_form": login_form})
    else:
        login_form = my_forms.LoginForm(request.POST)
        if not login_form.is_valid():
            return render(request, 'login.html', {"login_form": login_form})
        else:
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            user_obj = rbac_models.User.objects.filter(username=username, password=password).first()
            if not user_obj:
                return redirect(reverse('login'))
            else:
                init_permission(request, user_obj)

                # 根据不同的角色跳转到不同页面，这里仅做测试，不应该出现类似app01的硬编码
                department_id = user_obj.userinfo.department_id
                if department_id == 1000:
                    return redirect(reverse('app01_customer_mine'))
                elif department_id == 1001:
                    pass
                return redirect(reverse('app01_courserecord_changelist'))


def logout(request):
    """注销"""

    request.session.flush()
    return redirect(reverse('login'))


def index(request):
    """主页"""
    return render(request, 'index.html')
