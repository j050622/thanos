import os
import sys
import django

sys.path.append(r'D:\Python Code\CRM')

os.chdir(r'D:\Python Code\CRM')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CRM.settings")
django.setup()

from app03 import models

# customer_obj_list = models.Customer.objects.all()
# for obj in customer_obj_list:
#     print(obj)


# 筛选超时用户，更改其状态，置为公共资源
