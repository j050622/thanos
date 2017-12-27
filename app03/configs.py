"""
在crm中注册表时的自定义配置项
"""
import datetime

from django.conf.urls import url, include
from django.shortcuts import render, redirect, reverse, HttpResponse
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.forms import ModelForm, Form, fields, widgets
from django.db.models import Q

from thanos.service import crm
from . import models


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
    show_add_btn = True

    def sub_del_view(self, request, customer_id, course_id):
        """删除用户不感兴趣的课程"""
        models.Customer.objects.filter(pk=customer_id).first().course.remove(course_id)

        next_to = request.GET.get(self.query_dict_key)
        if next_to:
            return redirect('%s?%s' % (self.get_changelist_url(), next_to))
        else:
            return redirect('%s' % self.get_changelist_url())

    def public_source_view(self, request):
        if request.method == 'GET':
            date_now = datetime.date.today()
            delta_day0 = datetime.timedelta(days=15)
            delta_day1 = datetime.timedelta(days=3)

            compare_recv = date_now - delta_day0
            compare_follow = date_now - delta_day1

            recv_ot = Q(recv_date__lt=compare_recv)  # 15天未成单
            follow_ot = Q(last_consult_date__lt=compare_follow)  # 3天未跟进

            customer_obj_list = models.Customer.objects.filter(recv_ot | follow_ot, status=2).exclude(consultant_id=2)

            return render(request, 'public_source_customer.html', {"obj_list": customer_obj_list})

    def extra_urls(self):
        info = (self.app_label, self.model_name)
        urlpatterns = [
            url(r'^(\d+)/(\d+)/sub_del/$', self.wrap(self.sub_del_view), name='%s_%s_sub_del' % info),  # 删除咨询课程
            url(r'^public/$', self.wrap(self.public_source_view), name='%s_%s_public' % info),  # 公共资源
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
            return '顾问接单日期'
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
        ###这里可以从session中获取当前登录用户的id，如果当前用户记录的跟进人id不是登录用户id，下面可以返回“无权查看”
        ### 模拟用户星星已经登录
        current_user_id = 2  # 模拟从session中获取当前用户id
        res = models.Customer.objects.filter(pk=obj.id, consultant_id=current_user_id).exists()
        if not res:
            return '--'

        base_url = reverse('app03_consultrecord_changelist')
        return mark_safe('<a href="{}?customer_id={}" target="_blank">记录详情</a>'.format(base_url, obj.id))

    list_display = ['name', display_gender, display_course, display_status, display_consultant, display_recv_date,
                    display_consult_record]
    list_editable = ['name']


class ConsultRecordConfig(crm.CrmConfig):

    def changelist_view(self, request, *args, **kwargs):
        ### 模拟用户星星已经登录
        current_user_id = 2  # 模拟从session中获取当前用户id
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

        else:
            print(request.POST)
            return HttpResponse('post个人成绩')

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
    list_display = [display_date, display_course, display_student, display_record, ]

    show_actions = True
    actions_funcs = [multi_checked, multi_vacate, multi_late, multi_absence, multi_leave_early]


class PaymentRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = []
