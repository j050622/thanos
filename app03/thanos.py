"""
在crm中注册表
"""

from thanos.service import crm
from . import models
from .configs import configs, customer_config

crm.site.register(models.Department, configs.DepartmentConfig)
crm.site.register(models.UserInfo, configs.UserInfoConfig)
crm.site.register(models.School, configs.SchoolConfig)
crm.site.register(models.Course, configs.CourseConfig)
crm.site.register(models.ClassList, configs.ClassListConfig)
crm.site.register(models.Customer, customer_config.CustomerConfig)  # 注意路径
crm.site.register(models.CustomerDistribution, configs.CustomerDistributionConfig)
crm.site.register(models.ConsultantWeight, configs.ConsultantWeightConfig)
crm.site.register(models.ConsultRecord, configs.ConsultRecordConfig)
crm.site.register(models.PaymentRecord, configs.PaymentRecordConfig)
crm.site.register(models.Student, configs.StudentConfig)
crm.site.register(models.CourseRecord, configs.CourseRecordConfig)
crm.site.register(models.StudyRecord, configs.StudyRecordConfig)
