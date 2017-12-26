"""
在crm中注册表
"""

from thanos.service import crm
from . import models, configs

crm.site.register(models.Role)

crm.site.register(models.Department, configs.DepartmentConfig)

crm.site.register(models.UserInfo, configs.UserInfoConfig)
