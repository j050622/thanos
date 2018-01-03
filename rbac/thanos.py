from thanos.service import crm
from . import models
from . import configs

crm.site.register(models.Menu, configs.MenuConfig)
crm.site.register(models.PermissionGroup, configs.PermissionGroupConfig)
crm.site.register(models.Permission, configs.PermissionConfig)
crm.site.register(models.Role, configs.RoleConfig)
crm.site.register(models.User, configs.UserConfig)
