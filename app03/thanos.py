from thanos.service import crm
from app03 import models


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


class CourseConfig(crm.CrmConfig):
    show_add_btn = True
    list_display = ['name']
    list_editable = ['name']


class SchoolConfig(crm.CrmConfig):
    show_add_btn = True
    list_display = ['title']
    list_editable = ['title']


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


class CustomerConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = ['title']


class ConsultRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = ['title']


class PaymentRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = ['title']


class StudentConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = ['title']


class CourseRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = ['title']


class StudyRecordConfig(crm.CrmConfig):
    show_add_btn = True
    list_editable = ['title']


crm.site.register(models.Department, DepartmentConfig)
crm.site.register(models.UserInfo, UserInfoConfig)
crm.site.register(models.Course, CourseConfig)
crm.site.register(models.School, SchoolConfig)
crm.site.register(models.ClassList, ClassListConfig)
crm.site.register(models.Customer, CustomerConfig)
crm.site.register(models.ConsultRecord, ConsultRecordConfig)
crm.site.register(models.PaymentRecord, PaymentRecordConfig)
crm.site.register(models.Student, StudentConfig)
crm.site.register(models.CourseRecord, CourseRecordConfig)
crm.site.register(models.StudyRecord, StudentConfig)
