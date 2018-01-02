from thanos.service import crm
from . import models

crm.site.register(models.Menu)
crm.site.register(models.PermissionGroup)
crm.site.register(models.Permission)
crm.site.register(models.Role)
crm.site.register(models.User)
