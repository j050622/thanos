from django.db import models
from rbac import models as rbac_models


class School(models.Model):
    """
    校区表
    如：
        北京海淀校区
        北京昌平校区
        上海虹口校区
        广州白云山校区
    """
    title = models.CharField(verbose_name='校区名称', max_length=32)

    class Meta:
        pass

    def __str__(self):
        return self.title


class Department(models.Model):
    """
    部门表
    市场部     1000
    销售      1001
    """
    title = models.CharField(verbose_name='部门名称', max_length=16)
    code = models.IntegerField(verbose_name='部门编号', unique=True, null=False)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """
    员工表
    """
    auth_user = models.OneToOneField(verbose_name='关联账户', to=rbac_models.User)
    name = models.CharField(verbose_name='员工姓名', max_length=16)
    gender_choices = [(1, '男'), (2, '女')]
    gender = models.IntegerField(verbose_name='性别', choices=gender_choices)
    email = models.EmailField(verbose_name='邮箱', max_length=64)
    wechat_id = models.CharField(verbose_name='微信ID', max_length=32, null=True, blank=True)

    department = models.ForeignKey(verbose_name='部门', to="Department", to_field="code")

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    课程表
    如：
        Linux基础
        Linux架构师
        Python自动化开发精英班
        Python自动化开发架构师班
    """
    name = models.CharField(verbose_name='课程名称', max_length=32)

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """
    班级表
    如：
        Python全栈  面授班  5期  10000  2017-11-11  2018-5-11
    """
    school = models.ForeignKey(verbose_name='校区', to='School')
    course = models.ForeignKey(verbose_name='课程名称', to='Course')

    semester = models.IntegerField(verbose_name="班级(期)")
    price = models.IntegerField(verbose_name="学费")
    start_date = models.DateField(verbose_name="开班日期")
    graduate_date = models.DateField(verbose_name="结业日期", null=True, blank=True)
    instruction = models.CharField(verbose_name='说明', max_length=256, null=True, blank=True)
    teachers = models.ManyToManyField(verbose_name='任课老师', to='UserInfo', related_name='teach_classes',
                                      limit_choices_to={"department_id__in": [1003, 1004, 1005]})
    headmaster = models.ForeignKey(verbose_name='班主任', to='UserInfo', related_name='manage_classes',
                                   limit_choices_to={"department_id": 1002})

    def __str__(self):
        return "{}({}期)".format(self.course.name, self.semester)


class Customer(models.Model):
    """
    客户表
    """

    name = models.CharField(verbose_name='客户姓名', max_length=16)
    gender_choices = [(1, '男'), (2, '女')]
    gender = models.SmallIntegerField(verbose_name='性别', choices=gender_choices, default=1)
    qq = models.CharField(verbose_name='qq', max_length=64, unique=True, help_text='QQ号必须唯一')

    education_choices = [(1, '重点大学'),
                         (2, '普通本科'),
                         (3, '独立院校'),
                         (4, '民办本科'),
                         (5, '大专'),
                         (6, '民办专科'),
                         (7, '高中'),
                         (8, '其他')]

    education = models.IntegerField(verbose_name='学历', choices=education_choices, null=True, blank=True)
    graduation_school = models.CharField(verbose_name='毕业学校', max_length=64, null=True, blank=True)
    major = models.CharField(verbose_name='所学专业', max_length=64, null=True, blank=True)

    experience_choices = [
        (1, '在校生'),
        (2, '应届毕业'),
        (3, '半年以内'),
        (4, '半年至一年'),
        (5, '一年至三年'),
        (6, '三年至五年'),
        (7, '五年以上'),
    ]
    experience = models.IntegerField(verbose_name='工作经验', choices=experience_choices, null=True, blank=True)
    work_status_choices = [
        (1, '在职'),
        (2, '无业')
    ]
    work_status = models.IntegerField(verbose_name="职业状态", choices=work_status_choices, null=True, blank=True)
    company = models.CharField(verbose_name="目前就职公司", max_length=64, null=True, blank=True)
    salary = models.CharField(verbose_name="当前薪资", max_length=64, null=True, blank=True)

    source_choices = [
        (1, "qq群"),
        (2, "内部转介绍"),
        (3, "官方网站"),
        (4, "百度推广"),
        (5, "360推广"),
        (6, "搜狗推广"),
        (7, "腾讯课堂"),
        (8, "广点通"),
        (9, "高校宣讲"),
        (10, "渠道代理"),
        (11, "51cto"),
        (12, "智汇推"),
        (13, "网盟"),
        (14, "DSP"),
        (15, "SEO"),
        (16, "其它"),
    ]
    source = models.SmallIntegerField('客户来源', choices=source_choices, default=1)
    referral_from = models.ForeignKey(verbose_name="转介绍自学员", to='self', null=True, blank=True,
                                      help_text=u"若此客户是转介绍自内部学员,请在此处选择内部学员姓名")
    course = models.ManyToManyField(verbose_name="咨询课程", to="Course")
    status_choices = [
        (1, "已报名"),
        (2, "未报名")
    ]
    status = models.IntegerField(verbose_name="报名状态", choices=status_choices, default=2, help_text=u"选择客户此时的状态")
    date = models.DateField(verbose_name="咨询日期", auto_now_add=True)
    consultant = models.ForeignKey(verbose_name="课程顾问", to='UserInfo', limit_choices_to={'department_id': 1000},
                                   null=True, blank=True)
    recv_date = models.DateField(verbose_name='顾问接单日期', null=True, blank=True)
    last_consult_date = models.DateField(verbose_name="最后跟进日期", null=True, blank=True)

    def __str__(self):
        # return "姓名:{0},QQ:{1}".format(self.name, self.qq)
        return self.name


class CustomerDistribution(models.Model):
    """
    客户-顾问关系表
    """
    dist_date = models.DateField(verbose_name='分配日期', auto_now_add=True)
    customer = models.ForeignKey(verbose_name='客户', to='Customer')
    consultant = models.ForeignKey(verbose_name='顾问', to='UserInfo', limit_choices_to={"department_id": 1000})

    status_choices = [
        (1, '正在跟进'),
        (2, '已成单'),
        (3, '15天未成单'),
        (4, '3天未跟进')
    ]
    status = models.IntegerField(verbose_name='状态', choices=status_choices, default=1)
    memo = models.CharField(verbose_name='更多信息', max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = '客户分配表'


class ConsultRecord(models.Model):
    """
    客户跟进记录
    """
    customer = models.ForeignKey(verbose_name="所咨询客户", to='Customer')
    consultant = models.ForeignKey(verbose_name="跟踪人", to='UserInfo')
    date = models.DateField(verbose_name="跟进日期", auto_now_add=True)
    note = models.TextField(verbose_name="跟进内容...")

    def __str__(self):
        return self.date.strftime('%Y-%m-%d')


class ConsultantWeight(models.Model):
    """课程顾问权重表"""
    consultant = models.ForeignKey(verbose_name='课程顾问', to='UserInfo', limit_choices_to={"department_id": 1000})
    cus_limit = models.IntegerField(verbose_name='最大分配客户数量')
    weight = models.IntegerField(verbose_name='权重')


class PaymentRecord(models.Model):
    """
    缴费记录
    """
    customer = models.ForeignKey(Customer, verbose_name="客户")

    class_list = models.ForeignKey(verbose_name="班级", to="ClassList", null=True, blank=True)

    pay_type_choices = [
        (1, "订金/报名费"),
        (2, "学费"),
        (3, "转班"),
        (4, "退学"),
        (5, "退款"),
    ]
    pay_type = models.IntegerField(verbose_name="费用类型", choices=pay_type_choices, default=1)
    paid_fee = models.IntegerField(verbose_name="费用数额", default=0)
    turnover = models.IntegerField(verbose_name="成交金额", null=True, blank=True)
    quote = models.IntegerField(verbose_name="报价金额", null=True, blank=True)
    note = models.TextField(verbose_name="备注", null=True, blank=True)
    date = models.DateTimeField(verbose_name="交款日期", auto_now_add=True)
    consultant = models.ForeignKey(verbose_name="负责老师", to='UserInfo', help_text=u"谁签的单就选谁")


class Student(models.Model):
    """
    学生表（已报名）
    """
    customer = models.OneToOneField(verbose_name='客户信息', to='Customer')

    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    emergency_contract = models.CharField(max_length=32, null=True, blank=True, verbose_name='紧急联系人')
    class_list = models.ManyToManyField(verbose_name="已报班级", to='ClassList', blank=True)

    company = models.CharField(verbose_name='公司', max_length=128, null=True, blank=True)
    location = models.CharField(verbose_name='所在区域', max_length=64, null=True, blank=True)
    position = models.CharField(verbose_name='岗位', max_length=64, null=True, blank=True)
    salary = models.IntegerField(verbose_name='薪资', null=True, blank=True)
    welfare = models.CharField(verbose_name='福利', max_length=256, null=True, blank=True)
    date = models.DateField(verbose_name='入职时间', help_text='格式yyyy-mm-dd', null=True, blank=True)
    instruction = models.CharField(verbose_name='备注', max_length=256, null=True, blank=True)

    def __str__(self):
        return self.username


class CourseRecord(models.Model):
    """
    上课记录表
    """
    class_obj = models.ForeignKey(verbose_name="班级", to="ClassList")
    day_num = models.IntegerField(verbose_name="节次", help_text=u"此处填写第几节课或第几天课程,必须为数字")
    teacher = models.ForeignKey(verbose_name="讲师", to='UserInfo',
                                limit_choices_to={"department_id__in": [1003, 1004, 1005]})
    date = models.DateField(verbose_name="上课日期", auto_now_add=True)

    course_title = models.CharField(verbose_name='本节课程标题', max_length=64, null=True, blank=True)
    course_instruction = models.TextField(verbose_name='本节课程内容概要', null=True, blank=True)
    has_homework = models.BooleanField(default=True, verbose_name="本节有作业")
    homework_title = models.CharField(verbose_name='本节作业标题', max_length=64, null=True, blank=True)
    homework_instruction = models.TextField(verbose_name='作业描述', max_length=500, null=True, blank=True)
    exam = models.TextField(verbose_name='踩分点', max_length=300, null=True, blank=True)

    def __str__(self):
        return '{} - Day{}'.format(str(self.class_obj), self.day_num)


class StudyRecord(models.Model):
    course_record = models.ForeignKey(verbose_name="第几天课程", to="CourseRecord")
    student = models.ForeignKey(verbose_name="学员", to='Student')
    record_choices = [('checked', "已签到"),
                      ('vacate', "请假"),
                      ('late', "迟到"),
                      ('absence', "缺勤"),
                      ('leave_early', "早退"), ]
    record = models.CharField("上课记录", choices=record_choices, default="checked", max_length=64)
    score_choices = [(100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (70, 'B-'),
                     (60, 'C+'),
                     (50, 'C'),
                     (40, 'C-'),
                     (0, ' D'),
                     (-1, 'N/A'),
                     (-100, 'COPY'),
                     (-1000, 'FAIL'), ]
    score = models.IntegerField("本节成绩", choices=score_choices, default=-1)
    homework_note = models.CharField(verbose_name='作业评语', max_length=255, null=True, blank=True)
    note = models.CharField(verbose_name="备注", max_length=255, null=True, blank=True)

    homework = models.FileField(verbose_name='作业文件', null=True, blank=True, default=None)
    stu_instruction = models.TextField(verbose_name='学员备注', null=True, blank=True)
    date = models.DateTimeField(verbose_name='提交作业日期', auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(str(self.course_record), self.student)
