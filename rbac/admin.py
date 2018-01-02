from django.contrib import admin
from .models import Menu, PermissionGroup, Permission, Role, User

admin.site.register([Menu, PermissionGroup, Permission, Role, User])
