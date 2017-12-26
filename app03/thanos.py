"""
在crm中注册表
"""

from thanos.service import crm
from . import models, configs

crm.site.register(models.Department, configs.DepartmentConfig)
crm.site.register(models.UserInfo, configs.UserInfoConfig)
crm.site.register(models.School, configs.SchoolConfig)
crm.site.register(models.Course, configs.CourseConfig)
crm.site.register(models.ClassList, configs.ClassListConfig)
crm.site.register(models.Customer, configs.CustomerConfig)
crm.site.register(models.ConsultRecord, configs.ConsultRecordConfig)
crm.site.register(models.PaymentRecord, configs.PaymentRecordConfig)
crm.site.register(models.Student, configs.StudentConfig)
crm.site.register(models.CourseRecord, configs.CourseRecordConfig)
crm.site.register(models.StudyRecord, configs.StudyRecordConfig)
