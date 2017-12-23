from thanos.service import crm
from app03 import models

crm.site.register(models.Department)
crm.site.register(models.UserInfo)
crm.site.register(models.Course)
crm.site.register(models.School)
crm.site.register(models.ClassList)
crm.site.register(models.Customer)
crm.site.register(models.ConsultRecord)
crm.site.register(models.PaymentRecord)
crm.site.register(models.Student)
crm.site.register(models.CourseRecord)
crm.site.register(models.StudyRecord)
