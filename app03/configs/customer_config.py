"""
由于CustomerConfig内容较多，单独放在一个文件里
"""

import datetime
from urllib.request import quote

from django.conf.urls import url
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import StreamingHttpResponse, FileResponse
from django.utils.safestring import mark_safe
from django.db.transaction import atomic
from django.db.models import Q

from thanos.service import crm
from app03 import models
from app03 import permissions
from utils.customer_distribute.distribute import Distribute


class CustomerConfig(permissions.BasePermission, crm.CrmConfig):

    def add_view(self, request, *args, **kwargs):
        """
        重写添加记录方法，添加自动分配客户的功能
        """
        model_form = self.get_model_form_class()
        if request.method == 'GET':
            add_form = model_form()
            return render(request, 'thanos/add_view.html',
                          {"self": self, "add_form": add_form})
        else:
            add_form = model_form(data=request.POST)
            if not add_form.is_valid():
                return render(request, 'thanos/add_view.html',
                              {"self": self, "add_form": add_form})
            else:
                # 对新录入的客户进行自动分配
                consultant_id = Distribute.get_consultant_id()
                if not consultant_id:
                    return HttpResponse('课程顾问记录不详，不能进行自动分配')
                date_now = datetime.date.today()

                # 暂不提供销售主管指定课程顾问的功能，新录入的客户只能由系统自动分配
                try:
                    with atomic():
                        add_form.instance.consultant_id = consultant_id
                        add_form.instance.recv_date = date_now
                        add_form.instance.last_consult_date = date_now
                        new_obj = add_form.save()

                        # 创建客户分配记录
                        models.CustomerDistribution.objects.create(customer=new_obj, consultant_id=consultant_id)

                        # # 通过邮件、短信等方式向课程顾问发送通知
                        # from utils.notice import notice
                        # consultant_obj = models.UserInfo.objects.filter(pk=consultant_id).first()
                        # # to_name = consultant_obj.name
                        # # to_addr = consultant_obj.email
                        # # notice.send_notification(to_name, to_addr, '客户分配通知', '最新录入的客户已经自动分配')
                        # notice.send_notification('Mark', 'guixu2010@yeah.net', '客户分配通知', '最新录入的客户已经自动分配')###########
                        #
                        # from utils.notice import wechat
                        # wechat_id = 'oAKVr1secTVhwGZj8z5cIF3h91JI'  # 微信ID应该从数据库获取###########
                        # wechat.send_custom_msg(wechat_id, '发送内容测试...')
                        # wechat.send_template_msg(wechat_id, 'Jessica', 'Python全栈开发')  # 这里从数据库获取客户和课程等信息######

                        # 跳转
                        _popback_id = request.GET.get('popback_id')
                        if _popback_id:
                            from django.db.models.fields.reverse_related import ManyToOneRel

                            popback_info = {"status": None, "text": None, "value": None, "popback_id": _popback_id}

                            back_related_name = request.GET.get('related_name')
                            back_model_name = request.GET.get('model_name')

                            for rel_field_obj in new_obj._meta.related_objects:
                                # 遍历所有关联当前记录所在表的字段对象，例如：teachers、headmaster
                                _related_name = str(rel_field_obj.related_name)
                                _model_name = rel_field_obj.field.model._meta.model_name

                                if _related_name == back_related_name and _model_name == back_model_name:
                                    # 定位到打开popup的标签对应的字段
                                    _limit_choices_to = rel_field_obj.limit_choices_to

                                    if (type(rel_field_obj) == ManyToOneRel):
                                        _field_name = rel_field_obj.field_name
                                    else:
                                        # ManyToManyRel没有field_name方法，反应到models里面是因为没有to_field方法
                                        _field_name = 'pk'

                                    is_exists = self.model_class.objects.filter(pk=new_obj.pk,
                                                                                **_limit_choices_to).exists()
                                    if is_exists:
                                        # 如果新记录对象符合原limit_choices_to的条件
                                        popback_info["status"] = True
                                        popback_info["text"] = str(new_obj)
                                        popback_info["value"] = getattr(new_obj, _field_name)

                                        return render(request, 'thanos/popUp_response.html',
                                                      {"popback_info": json.dumps(popback_info)})

                            return render(request, 'thanos/popUp_response.html',
                                          {"popback_info": json.dumps(popback_info)})

                        else:
                            next_to = request.GET.get(self.query_dict_key)
                            if next_to:
                                return redirect('%s?%s' % (self.get_changelist_url(), next_to))
                            else:
                                return redirect('%s' % self.get_changelist_url())

                except Exception as e:
                    print('错误:', e)
                    Distribute.rollback(consultant_id)

    def multi_add_view(self, request, *args, **kwargs):
        """批量导入客户信息，添加到数据库"""
        if request.method == 'GET':
            return render(request, 'multi_add_view.html')
        else:
            file_obj = request.FILES.get('customers')
            file_name = file_obj.name
            file_bytes = file_obj.file
            # file_size = file_obj.size

            extension = file_name.rsplit('.', 1)[1]
            if extension not in ['xls', 'xlsx']:
                return HttpResponse('文件类型不合法')

            from utils.excel_handler.handler import handle
            handle(file_bytes.getvalue())  # 处理excel文件

            next_to = request.GET.get(self.query_dict_key)
            if next_to:
                return redirect('%s?%s' % (self.get_changelist_url(), next_to))
            else:
                return redirect('%s' % self.get_changelist_url())

    def download_tem(self, request, *args, **kwargs):
        """下载“批量导入客户信息”模板"""

        def file_iterator(file_path):
            with open(file_path, 'rb') as f:
                for chunk in f:
                    yield chunk

        file_path = 'static/files/批量导入客户.xlsx'
        res = FileResponse(file_iterator(file_path), content_type='application/octet-stream')
        res['Content-Disposition'] = 'attachment;filename={0}'.format(quote(file_path.rsplit('/', 1)[1]))
        return res

    def sub_del_view(self, request, customer_id, course_id):
        """删除用户不感兴趣的课程"""
        models.Customer.objects.filter(pk=customer_id).first().course.remove(course_id)

        next_to = request.GET.get(self.query_dict_key)
        if next_to:
            return redirect('%s?%s' % (self.get_changelist_url(), next_to))
        else:
            return redirect('%s' % self.get_changelist_url())

    def public_source_view(self, request):
        """从数据库中筛选出“超时”的客户，在页面显示，当前登录的课程顾问无法查看自己超时的客户"""

        date_now = datetime.date.today()
        current_userinfo_id = request.session.get('userinfo').get('id')

        compare_recv = date_now - datetime.timedelta(days=15)  # 15天未成单
        obj_list1 = models.Customer.objects.filter(
            Q(recv_date__lt=compare_recv), status=2).exclude(
            consultant_id=current_userinfo_id)
        for obj in obj_list1:
            models.CustomerDistribution.objects.filter(customer=obj).update(status=3)

        compare_follow = date_now - datetime.timedelta(days=3)  # 3天未跟进
        obj_list2 = models.Customer.objects.filter(
            Q(last_consult_date__lt=compare_follow), status=2).exclude(
            consultant_id=current_userinfo_id)
        for obj in obj_list2:
            models.CustomerDistribution.objects.filter(customer=obj).update(status=4)

        customer_obj_list = obj_list1 | obj_list2
        customer_obj_list = customer_obj_list.distinct()

        return render(request, 'public_source.html', {"obj_list": customer_obj_list})

    def mine_view(self, request):
        """显示当前登录的课程顾问的客户列表"""
        obj_list = models.Customer.objects.filter(consultant_id=request.session.get('userinfo').get('id'))
        return render(request, 'my_customer.html', {"obj_list": obj_list})

    def competition(self, request, customer_id):
        """对于公共资源，课程顾问进行手动抢单"""
        current_userinfo_id = request.session.get('userinfo').get('id')

        date_now = datetime.date.today()

        compare_recv = date_now - datetime.timedelta(days=15)  # 15天未成单
        compare_follow = date_now - datetime.timedelta(days=3)  # 3天未跟进

        rows = models.Customer.objects.filter(
            Q(recv_date__lt=compare_recv) | Q(last_consult_date__lt=compare_follow),
            status=2, pk=customer_id).exclude(consultant_id=2).update(recv_date=date_now, last_consult_date=date_now,
                                                                      consultant_id=current_userinfo_id)

        # 这里应该判断当前被更新状态的客户记录，状态是3天未跟进还是15天未成单，下面分配记录更新时作参考
        if not rows:
            return HttpResponse('手速太慢了')

        models.CustomerDistribution.objects.filter(customer_id=customer_id).update(status=3)  # 模拟3天未跟进
        models.CustomerDistribution.objects.create(dist_date=date_now, customer_id=customer_id,
                                                   consultant_id=current_userinfo_id)

        return redirect('%s_%s_public' % (self.app_label, self.model_name))

    def extra_urls(self):
        info = (self.app_label, self.model_name)
        urlpatterns = [
            url(r'^multi_add/$', self.wrap(self.multi_add_view), name='%s_%s_multi_add' % info),  # 批量导入客户信息
            url(r'^multi_add/download_tem/$', self.wrap(self.download_tem), name='download_tem'),
            url(r'^(\d+)/(\d+)/sub_del/$', self.wrap(self.sub_del_view), name='%s_%s_sub_del' % info),  # 删除咨询的课程
            url(r'^public/$', self.wrap(self.public_source_view), name='%s_%s_public' % info),  # 展示公共资源
            url(r'^mine/$', self.wrap(self.mine_view), name='%s_%s_mine' % info),  # 当前登录的课程顾问的客户列表
            url(r'^(\d+)/competition/$', self.wrap(self.competition)),  # 手动抢单
        ]
        return urlpatterns

    ## list_display中的方法 ##
    def display_gender(self, obj=None, is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()

    def display_education(self, obj=None, is_header=False):
        if is_header:
            return '学历'
        return obj.get_education_display()

    def display_experience(self, obj=None, is_header=False):
        if is_header:
            return '工作经验'
        return obj.get_experience_display()

    def display_work_status(self, obj=None, is_header=False):
        if is_header:
            return '职业状态'
        return obj.get_work_status_display()

    def display_source(self, obj=None, is_header=False):
        if is_header:
            return '客户来源'
        return obj.get_source_display()

    def display_referral_from(self, obj=None, is_header=False):
        # 转介绍的学员，待修改
        if is_header:
            return '转介绍学员'
        if obj.referral_from:
            return obj.referral_from.name
        else:
            return '无'

    def display_course(self, obj=None, is_header=False):
        """显示用户感兴趣的课程，支持点击删除"""
        if is_header:
            return '咨询课程'

        tmp_list = []
        info = (self.app_label, self.model_name)
        for i in obj.course.all():
            # del_href = '/crm/app03/customer/{}/{}/sub_del/'.format(obj.pk, i.pk)
            del_href = reverse('%s_%s_sub_del' % info, args=(obj.pk, i.pk))
            ele_html = '<a class="courses" href="{}">{}&nbsp;' \
                       '<span class="glyphicon glyphicon-remove"></span>' \
                       '</a>'.format(del_href, i.name)
            tmp_list.append(ele_html)
        return mark_safe('\n'.join(tmp_list))

    def display_status(self, obj=None, is_header=False):
        if is_header:
            return '报名状态'
        return obj.get_status_display()

    def display_consultant(self, obj=None, is_header=False):
        if is_header:
            return '课程顾问'
        return obj.consultant.name

    def display_date(self, obj=None, is_header=False):
        if is_header:
            return '咨询日期'
        return obj.date.strftime('%Y-%m-%d')

    def display_recv_date(self, obj=None, is_header=False):
        if is_header:
            return '课程顾问接单日期'
        recv_date = obj.recv_date
        if not recv_date:
            return '-'
        else:
            return obj.recv_date.strftime('%Y-%m-%d')

    def display_last_consult_date(self, obj=None, is_header=False):
        if is_header:
            return '最后跟进日期'
        return obj.last_consult_date.strftime('%Y-%m-%d')

    def display_consult_record(self, obj=None, is_header=False):
        """生成记录详情按钮，点击跳转到该条记录对应的用户的跟进记录"""
        if is_header:
            return '跟进记录'

        base_url = reverse('app03_consultrecord_changelist')
        return mark_safe('<a href="{}?customer_id={}" target="_blank">记录详情</a>'.format(base_url, obj.id))

    # actions中的方法
    def multi_del(self, request):
        """批量删除"""
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()

    multi_del.short_desc = '批量删除'

    ###
    order_by_condition = ['-status', ]
    list_display = ['name', display_gender, display_course, display_status, display_consultant, display_recv_date,
                    display_last_consult_date, display_consult_record]
    list_editable = ['name']
    list_per_page = 20
    show_actions = True
    actions_funcs = [multi_del]
