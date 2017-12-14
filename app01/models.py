from django.db import models


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=16, verbose_name='角色名')

    class Meta:
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    """用户信息表"""
    username = models.CharField(max_length=16, verbose_name='用户名')

    class Meta:
        verbose_name_plural = '用户信息表'

    def __str__(self):
        return self.username
