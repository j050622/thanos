"""
在crm中注册表时的自定义配置项
"""
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
from utils.customer_distribute.distribute import Distribute


class DepartmentConfig(crm.CrmConfig):
    show_add_btn = True
    list_display = ['title', 'code']
    list_editable = ['title']


class UserInfoConfig(crm.CrmConfig):
    show_add_btn = True

    def display_department(self, obj=None, is_header=False):
        """显示员工所在部门的名称"""
        if is_header:
            return '部门'
        return obj.department.title

    list_display = ['name', 'email', display_department]
    list_editable = ['name']
    comb_filter_rows = [
        crm.FilterRowOption('department', func_get_val=lambda obj: str(obj.code))]  # 关联字段不是pk而是code
    show_comb_filter = True


class SchoolConfig(crm.CrmConfig):
    show_add_btn = True
    list_display = ['title']
    list_editable = ['title']


class CourseConfig(crm.CrmConfig):
    show_add_btn = True
    list_display = ['name']
    list_editable = ['name']


class ClassListConfig(crm.CrmConfig):
    show_add_btn = True

    def display_classname(self, obj=None, is_header=False):
        """拼接课程名和学期数，如Python全栈（6期）"""
        if is_header:
            return '班级名'
        return '%s(%s期)' % (obj.course.name, obj.semester)

    def display_stu_cnt(self, obj=None, is_header=False):
        """班级人数"""
        if is_header:
            return '班级人数'
        return obj.student_set.count()

    def display_teachers(self, obj=None, is_header=False):
        """显示所有任课教师"""
        if is_header:
            return '任课教师'
        tmp_list = [i.name for i in obj.teachers.all()]
        return ','.join(tmp_list)

    def display_start_date(self, obj=None, is_header=False):
        """格式化输出开班日期"""
        if is_header:
            return '开班日期'
        return obj.start_date.strftime('%Y-%m-%d')

    list_display = ['school', display_classname, display_stu_cnt, 'headmaster', display_teachers, display_start_date,
                    'price']
    list_editable = [display_classname]
    comb_filter_rows = [crm.FilterRowOption('school'), crm.FilterRowOption('course')]
    show_comb_filter = True


class CustomerConfig(crm.CrmConfig):

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

                except Exception as e:
                    print('错误:', e)
                    Distribute.rollback(consultant_id)

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

                            is_exists = self.model_class.objects.filter(pk=new_obj.pk, **_limit_choices_to).exists()
                            if is_exists:
                                # 如果新记录对象符合原limit_choices_to的条件
                                popback_info["status"] = True
                                popback_info["text"] = str(new_obj)
                                popback_info["value"] = getattr(new_obj, _field_name)

                                return render(request, 'thanos/popUp_response.html',
                                              {"popback_info": json.dumps(popback_info)})

                    return render(request, 'thanos/popUp_response.html', {"popback_info": json.dumps(popback_info)})
                else:
                    next_to = request.GET.get(self.query_dict_key)
                    if next_to:
                        return redirect('%s?%s' % (self.get_changelist_url(), next_to))
                    else:
                        return redirect('%s' % self.get_changelist_url())

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
        res = StreamingHttpResponse(file_iterator(file_path), content_type='application/octet-stream')
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
        current_user_id = request.session.get('userinfo').get('id')

        compare_recv = date_now - datetime.timedelta(days=15)  # 15天未成单
        obj_list1 = models.Customer.objects.filter(
            Q(recv_date__lt=compare_recv), status=2).exclude(
            consultant_id=current_user_id)
        for obj in obj_list1:
            models.CustomerDistribution.objects.filter(customer=obj).update(status=3)

        compare_follow = date_now - datetime.timedelta(days=3)  # 3天未跟进
        obj_list2 = models.Customer.objects.filter(
            Q(last_consult_date__lt=compare_follow), status=2).exclude(
            consultant_id=current_user_id)
        for obj in obj_list2:
            models.CustomerDistribution.objects.filter(customer=obj).update(status=4)

        customer_obj_list = obj_list1 | obj_list2
        customer_obj_list = customer_obj_list.distinct()

        return render(request, 'public_source_customer.html', {"obj_list": customer_obj_list})

    def mine_view(self, request):
        """显示当前登录的课程顾问的客户列表"""
        obj_list = models.Customer.objects.filter(consultant_id=request.session.get('userinfo').get('id'))
        return render(request, 'my_customer.html', {"obj_list": obj_list})

    def competition(self, request, stu_id):
        """对于公共资源，课程顾问进行手动抢单"""
        current_user_id = request.session.get('userinfo').get('id')

        date_now = datetime.date.today()

        compare_recv = date_now - datetime.timedelta(days=15)  # 15天未成单
        compare_follow = date_now - datetime.timedelta(days=3)  # 3天未跟进

        rows = models.Customer.objects.filter(
            Q(recv_date__lt=compare_recv) | Q(last_consult_date__lt=compare_follow),
            status=2, pk=stu_id).exclude(consultant_id=2).update(recv_date=date_now, last_consult_date=date_now,
                                                                 consultant_id=current_user_id)
        if not rows:
            return HttpResponse('手速太慢了')

        models.CustomerDistribution.objects.filter(customer_id=stu_id).update(status=3)  # 模拟3天未跟进
        models.CustomerDistribution.objects.create(dist_date=date_now, customer_id=stu_id,
                                                   consultant_id=current_user_id)

        return redirect('%s_%s_public' % (self.app_label, self.model_name))

    def extra_urls(self):
        info = (self.app_label, self.model_name)
        urlpatterns = [
            url(r'^multi_add$', self.wrap(self.multi_add_view), name='%s_%s_multi_add' % info),  # 批量导入客户信息
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

        current_user_id = self.request.session.get('userinfo').get('id')
        res = models.Customer.objects.filter(pk=obj.id, consultant_id=current_user_id).exists()
        if not res:
            return '--'

        base_url = reverse('app03_consultrecord_changelist')
        return mark_safe('<a href="{}?customer_id={}" target="_blank">记录详情</a>'.format(base_url, obj.id))

    ##actions中的方法
    def multi_del(self, request):
        """批量删除"""
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(pk__in=pk_list).delete()

    multi_del.short_desc = '批量删除'

    ###
    show_add_btn = True
    order_by_condition = ['-status', ]
    list_display = ['name', display_gender, display_course, display_status, display_consultant, display_recv_date,
                    display_last_consult_date, display_consult_record]
    list_editable = ['name']
    list_per_page = 20
    show_actions = True
    actions_funcs = [multi_del]


class CustomerDistributionConfig(crm.CrmConfig):

    def display_dist_date(self, obj=None, is_header=False):
        if is_header:
            return '分配日期'
        return obj.dist_date.strftime('%Y-%m-%d')

    def display_customer(self, obj=None, is_header=False):
        if is_header:
            return '客户'
        return obj.customer.name

    def display_consultant(self, obj=None, is_header=False):
        if is_header:
            return '课程顾问'
        return obj.consultant.name

    def display_status(self, obj=None, is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()

    list_display = [display_dist_date, display_customer, display_consultant, display_status]
    list_per_page = 20


class ConsultRecordConfig(crm.CrmConfig):

    def changelist_view(self, request, *args, **kwargs):
        # 重写changelist_view，在其中模拟用户星星已经登录
        current_user_id = request.session.get('userinfo').get('id')
        customer_id = request.GET.get('customer_id')
        if not customer_id:
            return HttpResponse('参数错误，请关闭页面后重试')
        else:
            res = models.Customer.objects.filter(pk=customer_id, consultant_id=current_user_id).exists()
            if not res:
                return HttpResponse('无权查看')

        return super().changelist_view(request, *args, **kwargs)

    show_add_btn = True

    def display_consultant(self, obj=None, is_header=False):
        if is_header:
            return '跟进人'
        return obj.consultant.name

    list_display = ['date', 'note', display_consultant]
    list_editable = ['date']


class StudentConfig(crm.CrmConfig):
    show_add_btn = True

    def check_score_view(self, request, pk):
        """查看个人成绩视图"""
        if request.method == 'GET':
            student_obj = models.Student.objects.filter(pk=pk).first()
            if not student_obj:
                return HttpResponse('查无此人')

            class_list = student_obj.class_list.all()
            return render(request, 'check_score_view.html', {"class_list": class_list, "stu_id": pk})

    def chart_view(self, request):
        """个人成绩图表,ajax请求"""
        if request.is_ajax():
            stu_id = request.GET.get('sid')
            cls_id = request.GET.get('cid')
            res_dict = {"status": None, "error_msg": None, "data_list": [], "class_name": None}

            try:
                study_record_list = models.StudyRecord.objects.filter(student_id=stu_id,
                                                                      course_record__class_obj_id=cls_id)
                for study_record_obj in study_record_list:
                    day_n = 'day{}'.format(study_record_obj.course_record.day_num)
                    score = study_record_obj.score

                    res_dict["data_list"].append([day_n, score])
                res_dict["status"] = True
                res_dict["class_name"] = str(models.ClassList.objects.filter(pk=cls_id).first())

            except Exception as e:
                res_dict["status"] = False
                res_dict["error_msg"] = str(e)

            return JsonResponse(res_dict)

    def extra_urls(self):
        """添加查看个人成绩及相关的URL"""
        info = (self.app_label, self.model_name)
        urlpatterns = [
            url(r'^(\d+)/check_score/$', self.wrap(self.check_score_view), name='%s_%s_check_score' % info),
            url(r'^chart/$', self.wrap(self.chart_view), name='%s_%s_chart' % info),
        ]
        return urlpatterns

    ## list_display中的方法 ##
    def display_name(self, obj=None, is_header=False):
        if is_header:
            return '学生姓名'
        return obj.customer.name

    def display_class_list(self, obj=None, is_header=False):
        if is_header:
            return '所在班级'

        tmp_list = []
        for i in obj.class_list.all():
            tmp_list.append('{}({}期)'.format(i.course.name, i.semester))
        return ' | '.join(tmp_list)

    def display_check_score(self, obj=None, is_header=False):
        if is_header:
            return '查看个人成绩'

        base_url = reverse('%s_%s_check_score' % (self.app_label, self.model_name), args=(obj.pk,))
        return mark_safe('<a href="{}">查看个人成绩</a>'.format(base_url))

    list_display = [display_name, display_class_list, display_check_score, 'emergency_contract', ]
    list_editable = [display_name]


class CourseRecordConfig(crm.CrmConfig):
    show_add_btn = True

    def resultinput_view(self, request, course_record_id):
        """成绩录入视图"""
        if request.method == 'GET':
            study_record_obj_list = models.StudyRecord.objects.filter(course_record_id=course_record_id)
            data_list = []
            for stu_record_obj in study_record_obj_list:
                tmp_dict = {"stu_record_obj": stu_record_obj, "form": None}

                TempForm = type('TempForm', (Form,), {
                    "score_{}".format(stu_record_obj.pk): fields.ChoiceField(
                        choices=stu_record_obj.score_choices,
                        widget=widgets.Select(attrs={"class": 'form-control'})),
                    "homework_note_{}".format(stu_record_obj.pk): fields.CharField(
                        widget=widgets.TextInput(attrs={"class": 'form-control'}))
                })

                tmp_dict["form"] = TempForm(initial={
                    "score_{}".format(stu_record_obj.pk): stu_record_obj.score,
                    "homework_note_{}".format(stu_record_obj.pk): stu_record_obj.homework_note,
                })
                data_list.append(tmp_dict)

            return render(request, 'resultinput_view.html', {"data_list": data_list})
        else:
            tmp_dict = {}
            for field_and_pk, value in request.POST.items():
                if field_and_pk == 'csrfmiddlewaretoken':
                    continue
                field, pk = field_and_pk.rsplit('_', 1)
                if pk not in tmp_dict:
                    tmp_dict[pk] = {field: value}
                else:
                    tmp_dict[pk][field] = value

            for pk, dict_item in tmp_dict.items():
                models.StudyRecord.objects.filter(pk=pk).update(**dict_item)

            return redirect(reverse('%s_%s_changelist' % (self.app_label, self.model_name)))

    def extra_urls(self):
        """添加成绩录入的URL"""
        info = (self.app_label, self.model_name)
        urlpatterns = [
            url(r'^(\d+)/resultinput/$', self.wrap(self.resultinput_view), name='%s_%s_resultinput' % info),
        ]
        return urlpatterns

    ## list_display中的方法 ##
    def display_class_info(self, obj=None, is_header=False):
        if is_header:
            return '班级'
        return '{}({}期)'.format(obj.class_obj.course.name, obj.class_obj.semester)

    def display_teacher(self, obj=None, is_header=False):
        if is_header:
            return '讲师'
        return obj.teacher.name

    def display_date(self, obj=None, is_header=False):
        if is_header:
            return '上课日期'
        return obj.date.strftime('%Y-%m-%d')

    def display_check_on(self, obj=None, is_header=False):
        if is_header:
            return '考勤'
        return mark_safe(
            '<a href="/crm/{}/studyrecord/?course_record={}">查看考勤详情</a>'.format(self.app_label, obj.pk))

    def display_resultinput(self, obj=None, is_header=False):
        if is_header:
            return '录入成绩'
        info = (self.app_label, self.model_name)
        base_url = reverse('%s_%s_resultinput' % info, args=(obj.pk,))
        return mark_safe('<a href="%s">录入成绩</a>' % base_url)

    ## actions里的方法 ##
    def multi_init(self, request):
        pk_list = request.POST.getlist('pk')
        course_record_obj_list = models.CourseRecord.objects.filter(pk__in=pk_list)
        for record_obj in course_record_obj_list:
            is_exists = models.StudyRecord.objects.filter(course_record=record_obj).exists()
            if not is_exists:
                student_obj_list = models.Student.objects.filter(class_list=record_obj.class_obj)
                tmp_list = [models.StudyRecord(course_record=record_obj, student=stu_obj) for stu_obj in
                            student_obj_list]
                models.StudyRecord.objects.bulk_create(tmp_list)

    multi_init.short_desc = '初始化学生课堂记录'

    ######
    list_display = [display_class_info, 'day_num', display_teacher, display_date, 'course_title', display_check_on,
                    display_resultinput]
    list_editable = [display_class_info]
    show_actions = True
    actions_funcs = [multi_init, ]


class ConsultantWeightConfig(crm.CrmConfig):
    show_add_btn = True

    def display_consultant(self, obj=None, is_header=False):
        if is_header:
            return '课程顾问'
        return obj.consultant.name

    list_display = [display_consultant, 'cus_limit', 'weight']
    list_editable = [display_consultant]


class StudyRecordConfig(crm.CrmConfig):

    ## list_display中的方法 ##
    def display_date(self, obj=None, is_header=False):
        if is_header:
            return '上课日期'
        return obj.date.strftime('%Y-%m-%d')

    def display_course(self, obj=None, is_header=False):
        if is_header:
            return '课程'
        return '{}({}期) - Day{}'.format(obj.course_record.class_obj.course.name, obj.course_record.class_obj.semester,
                                        obj.course_record.day_num)

    def display_teacher(self, obj=None, is_header=False):
        if is_header:
            return '讲师'
        return obj.course_record.teacher.name

    def display_student(self, obj=None, is_header=False):
        if is_header:
            return '学生姓名'
        return obj.student.customer.name

    def display_record(self, obj=None, is_header=False):
        if is_header:
            return '出勤情况'
        return obj.get_record_display()

    ## actions的方法 ##
    def multi_checked(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(pk__in=pk_list).update(record='checked')

    multi_checked.short_desc = '签到'

    def multi_vacate(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(pk__in=pk_list).update(record='vacate')

    multi_vacate.short_desc = '请假'

    def multi_late(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(pk__in=pk_list).update(record='late')

    multi_late.short_desc = '迟到'

    def multi_absence(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(pk__in=pk_list).update(record='absence')

    multi_absence.short_desc = '缺勤'

    def multi_leave_early(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(pk__in=pk_list).update(record='leave_early')

    multi_leave_early.short_desc = '早退'

    ######
    list_display = [display_date, display_course, display_student, display_record]

    show_actions = True
    actions_funcs = [multi_checked, multi_vacate, multi_late, multi_absence, multi_leave_early]


class PaymentRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = []
