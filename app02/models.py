from django.db import models


class Role(models.Model):
    name = models.CharField(verbose_name='角色名', max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '角色表'


class Department(models.Model):
    caption = models.CharField(verbose_name='部门名称', max_length=23)

    def __str__(self):
        return self.caption

    class Meta:
        verbose_name_plural = '部门表'


class UserInfo(models.Model):
    username = models.CharField(verbose_name='姓名', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)

    gender_choices = (
        (1, '男'),
        (2, '女'),
    )
    gender = models.IntegerField(verbose_name='性别', choices=gender_choices)

    department = models.ForeignKey(verbose_name="所属部门", to='Department')
    roles = models.ManyToManyField(verbose_name="担任的角色", to='Role')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户信息表'
