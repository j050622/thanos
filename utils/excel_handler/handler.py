import datetime

import xlrd
from django.http import HttpResponse
from django.db.transaction import atomic

from app03 import models
from utils.customer_distribute.distribute import Distribute


def handle(file_contens):
    """处理excel，创建客户记录和客户分配记录"""

    workbook = xlrd.open_workbook(file_contents=file_contens)
    sheet = workbook.sheet_by_index(0)

    # 与数据库字段名一致
    maps = {
        0: 'name',
        1: 'gender',
        2: 'qq'
    }

    for index in range(1, sheet.nrows):
        row = sheet.row(index)
        tmp_dict = {}
        for i in range(len(maps)):
            tmp_dict[maps[i]] = row[i].value

        consultant_id = Distribute.get_consultant_id()  # 分配一个课程顾问
        if not consultant_id:
            return HttpResponse('课程顾问记录不详，不能进行自动分配')
        date_now = datetime.date.today()

        try:
            with atomic():
                customer_obj = models.Customer.objects.create(**tmp_dict, consultant_id=consultant_id,
                                                              recv_date=date_now, last_consult_date=date_now)
                models.CustomerDistribution.objects.create(customer=customer_obj,
                                                           consultant_id=customer_obj.consultant_id)
        except Exception as e:
            print('错误:', e)
            Distribute.rollback(consultant_id)
