from django.shortcuts import render, redirect, reverse
from django.http import StreamingHttpResponse

from . import my_forms
from . import models


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

            user_obj = models.UserInfo.objects.filter(username=username, password=password).first()
            if user_obj:
                department_id = user_obj.department_id
                tmp_dict = {"username": username, "id": user_obj.pk, "department_id": department_id}
                request.session["userinfo"] = tmp_dict

                if department_id == 1000:
                    return redirect(reverse('app03_customer_mine'))
                elif department_id == 1001:
                    pass
                else:
                    return redirect(reverse('app03_courserecord_changelist'))
            else:
                return redirect(reverse('login'))


def logout(request):
    """注销"""

    request.session.flush()
    return redirect(reverse('login'))
