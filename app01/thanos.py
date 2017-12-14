from django.utils.safestring import mark_safe

from thanos.service import crm
from app01 import models

crm.site.register(models.Role)
crm.site.register(models.UserInfo)
