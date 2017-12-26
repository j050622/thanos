"""
在crm中注册表时的自定义配置项
"""

from django.conf.urls import url, include
from django.utils.safestring import mark_safe
from django.forms import ModelForm, Form
from django.shortcuts import render, redirect, reverse, HttpResponse

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
        tmp = [i.name for i in obj.teachers.all()]
        return ','.join(tmp)

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

    def extra_urls(self):
        return [url(r'^(\d+)/(\d+)/sub_del/$', self.wrap(self.sub_del_view))]

    ### 页面展示相关 ###
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

        tmp = []
        for i in obj.course.all():
            del_href = '/crm/app03/customer/{}/{}/sub_del/'.format(obj.pk, i.pk)
            ele_html = '<a class="courses" href="{}">{}&nbsp;' \
                       '<span class="glyphicon glyphicon-remove"></span>' \
                       '</a>'.format(del_href, i.name)
            tmp.append(ele_html)
        return mark_safe('\n'.join(tmp))

    def display_status(self, obj=None, is_header=False):
        if is_header:
            return '报名状态'
        print(obj.get_status_display())
        return obj.get_status_display()

    def display_consultant(self, obj=None, is_header=False):
        if is_header:
            return '课程顾问'
        return obj.consultant.name

    def display_date(self, obj=None, is_header=False):
        if is_header:
            return '咨询日期'
        return obj.date.strftime('%Y-%m-%d')

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

    list_display = ['name', display_gender, display_course, display_status, display_consultant,
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


class PaymentRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = []


class StudentConfig(crm.CrmConfig):
    show_add_btn = True

    def display_name(self, obj=None, is_header=False):
        if is_header:
            return '学生姓名'
        return obj.customer.name

    def display_class_list(self, obj=None, is_header=False):
        if is_header:
            return '所在班级'

        tmp = []
        for i in obj.class_list.all():
            tmp.append('{}({}期)'.format(i.course.name, i.semester))
        return ' | '.join(tmp)

    def add_view(self, request, *args, **kwargs):
        """
        添加记录
        """
        model_form = self.get_model_form_class()
        if request.method == 'GET':
            add_edit_form = model_form()
            return render(request, 'thanos/add_view.html',
                          {"self": self, "add_edit_form": add_edit_form})
        else:
            _popback_id = request.GET.get('popback_id')
            add_edit_form = model_form(data=request.POST)

            if not add_edit_form.is_valid():
                return render(request, 'thanos/add_view.html',
                              {"self": self, "add_edit_form": add_edit_form})
            else:
                new_obj = add_edit_form.save()
                print(new_obj.customer.get_status_display())
                new_obj.customer.status = 1  # 自动更新报名状态
                print(new_obj.customer.get_status_display())

                if _popback_id:
                    from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel

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

    list_display = [display_name, display_class_list, 'emergency_contract', ]
    list_editable = []


class CourseRecordConfig(crm.CrmConfig):
    show_add_btn = True

    def display_class_list(self, obj=None, is_header=False):
        if is_header:
            return '班级'
        return '{}{}'.format(obj.class_obj.course.name, obj.class_obj.semester)

    list_display = [display_class_list, ]
    list_editable = [display_class_list, ]


class StudyRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_display = ['record', 'homework_note', 'note']
    list_editable = []
