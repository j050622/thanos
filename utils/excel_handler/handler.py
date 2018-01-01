import xlrd

from app03 import models


def handle(file_contens):
    workbook = xlrd.open_workbook(file_contents=file_contens)
    sheet = workbook.sheet_by_index(0)

    maps = {
        0: 'name',
        1: 'gender',
        2: 'qq'
    }

    obj_list = []
    for index in range(1, sheet.nrows):
        cells = sheet.row(index)
        tmp_dict = {}
        for i in range(len(maps)):
            tmp_dict[maps[i]] = cells[i].value

        obj_list.append(models.Customer(**tmp_dict))
    models.Customer.objects.bulk_create(obj_list)
    # 还有课程的多对多没有添加
