# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-01 19:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app03', '0015_userinfo_wechat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='gender',
            field=models.SmallIntegerField(choices=[(1, '男'), (2, '女')], default=1, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_consult_date',
            field=models.DateField(auto_now_add=True, verbose_name='最后跟进日期'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='recv_date',
            field=models.DateField(auto_now_add=True, verbose_name='顾问接单日期'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='work_status',
            field=models.IntegerField(blank=True, choices=[(1, '在职'), (2, '无业')], null=True, verbose_name='职业状态'),
        ),
    ]