"""
在crm中注册表
"""

from thanos.service import crm
from . import models, configs

crm.site.register(models.Role, configs.RoleConfig)
crm.site.register(models.UserInfo, configs.UserInfoConfig)
