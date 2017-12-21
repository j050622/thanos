from django.contrib import admin

from app02 import models

admin.site.register([models.Role, models.UserInfo, models.Department])
