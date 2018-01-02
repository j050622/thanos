from django.db import models


class Menu(models.Model):
    '''菜单表'''
    title = models.CharField(max_length=10, verbose_name='菜单名')

    class Meta:
        verbose_name_plural = '菜单组表 '

    def __str__(self):
        return self.title


class PermissionGroup(models.Model):
    '''权限组表'''
    title = models.CharField(max_length=10, verbose_name='权限组名')
    menu = models.ForeignKey(to='Menu', verbose_name='所属菜单')

    class Meta:
        verbose_name_plural = '权限组表'

    def __str__(self):
        return self.title


class Permission(models.Model):
    '''权限表'''
    title = models.CharField(max_length=10, verbose_name='权限名')
    url = models.CharField(max_length=64, verbose_name='含正则的URL')
    menu_ref = models.ForeignKey(to='Permission', null=True, blank=True, verbose_name='关联的菜单URL')
    code = models.CharField(max_length=10, verbose_name='组中别名')
    group = models.ForeignKey(to='PermissionGroup', verbose_name='所属权限组')

    class Meta:
        verbose_name_plural = '权限表'

    def __str__(self):
        return self.title


class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=10, verbose_name='角色名')
    permissions = models.ManyToManyField(to='Permission', verbose_name='拥有的权限')

    class Meta:
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.name


class User(models.Model):
    '''用户表'''
    username = models.CharField(max_length=16, verbose_name='用户名')
    password = models.CharField(max_length=16, verbose_name='密码')
    roles = models.ManyToManyField(to='Role', verbose_name='担任的角色', null=True, blank=True)

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username
